"""
Simplified VM code which works for some cases.
You need extend/rewrite code to pass all cases.
"""

import builtins
import dis
import operator
import types
import typing as tp

CO_VARARGS = 4
CO_VARKEYWORDS = 8


class Frame:
    """
    Frame header in cpython with description
        https://github.com/python/cpython/blob/3.13/Include/internal/pycore_frame.h

    Text description of frame parameters
        https://docs.python.org/3/library/inspect.html?highlight=frame#types-and-members
    """
    def __init__(self,
                 frame_code: types.CodeType,
                 frame_builtins: dict[str, tp.Any],
                 frame_globals: dict[str, tp.Any],
                 frame_locals: dict[str, tp.Any]) -> None:
        self.code = frame_code
        self.builtins = frame_builtins
        self.globals = frame_globals
        self.locals = frame_locals
        self.data_stack: list[tp.Any] = []
        self.return_value = None

        self.instructions = list(dis.get_instructions(self.code))
        self.offset_to_index: dict[int, int] = {instr.offset: idx for idx, instr in enumerate(self.instructions)}

        self.kw_names: tuple[str, ...] | None = None

        self.cells: dict[str, tp.Any] = {}

    def top(self) -> tp.Any:
        return self.data_stack[-1]

    def pop(self) -> tp.Any:
        return self.data_stack.pop()

    def push(self, *values: tp.Any) -> None:
        self.data_stack.extend(values)

    def popn(self, n: int) -> list[tp.Any]:
        if n > 0:
            returned = self.data_stack[-n:]
            self.data_stack[-n:] = []
            return returned
        else:
            return []

    def run(self) -> tp.Any:
        idx: int = 0
        while idx < len(self.instructions):
            instruction = self.instructions[idx]
            op_method = getattr(self, instruction.opname.lower() + "_op", None)

            if op_method is None:
                raise NotImplementedError(f"Operation {instruction.opname} is not implemented")

            result = op_method(instruction)

            if result is True:
                break
            elif isinstance(result, int):
                idx = self.offset_to_index[result]
            else:
                idx = int(idx) + 1

        return self.return_value

    def resume_op(self, instr: dis.Instruction) -> None:
        pass

    def nop_op(self, instr: dis.Instruction) -> None:
        pass

    def push_null_op(self, instr: dis.Instruction) -> None:
        self.push(None)

    def precall_op(self, instr: dis.Instruction) -> None:
        pass

    def load_const_op(self, instr: dis.Instruction) -> None:
        self.push(instr.argval)

    def load_fast_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        if name in self.locals:
            self.push(self.locals[name])
        else:
            raise UnboundLocalError(f"local variable '{name}' referenced before assignment")

    def load_name_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        if name in self.locals:
            self.push(self.locals[name])
        elif name in self.globals:
            self.push(self.globals[name])
        elif name in self.builtins:
            self.push(self.builtins[name])
        else:
            raise NameError(f"name '{name}' is not defined")

    def load_global_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        if name in self.globals:
            value = self.globals[name]
        elif name in self.builtins:
            value = self.builtins[name]
        else:
            raise NameError(f"name '{name}' is not defined")

        if instr.arg is not None and (instr.arg & 1):
            self.push(value)
            self.push(None)
        else:
            self.push(value)

    def store_fast_op(self, instr: dis.Instruction) -> None:
        self.locals[instr.argval] = self.pop()

    def store_name_op(self, instr: dis.Instruction) -> None:
        self.locals[instr.argval] = self.pop()

    def store_global_op(self, instr: dis.Instruction) -> None:
        self.globals[instr.argval] = self.pop()

    def delete_fast_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        if name in self.locals:
            del self.locals[name]
        else:
            raise UnboundLocalError(f"local variable '{name}' referenced before assignment")

    def delete_name_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        if name in self.locals:
            del self.locals[name]
        elif name in self.globals:
            del self.globals[name]
        else:
            raise NameError(f"name '{name}' is not defined")

    def delete_global_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        if name in self.globals:
            del self.globals[name]
        else:
            raise NameError(f"name '{name}' is not defined")

    def pop_top_op(self, instr: dis.Instruction) -> None:
        self.pop()

    def copy_op(self, instr: dis.Instruction) -> None:
        i = instr.argval
        self.push(self.data_stack[-i])

    def swap_op(self, instr: dis.Instruction) -> None:
        i = instr.argval
        self.data_stack[-1], self.data_stack[-i] = self.data_stack[-i], self.data_stack[-1]

    def binary_op_op(self, instr: dis.Instruction) -> None:
        op_code = instr.arg
        if op_code is None:
            raise ValueError("Binary operation requires arg")
        right = self.pop()
        left = self.pop()

        ops = [
            operator.add,
            operator.and_,
            operator.floordiv,
            operator.lshift,
            operator.matmul,
            operator.mul,
            operator.mod,
            operator.or_,
            operator.pow,
            operator.rshift,
            operator.sub,
            operator.truediv,
            operator.xor,
            operator.iadd,
            operator.iand,
            operator.ifloordiv,
            operator.ilshift,
            operator.imatmul,
            operator.imul,
            operator.imod,
            operator.ior,
            operator.ipow,
            operator.irshift,
            operator.isub,
            operator.itruediv,
            operator.ixor,
        ]

        if 0 <= op_code < len(ops):
            result = ops[op_code](left, right)
            self.push(result)
        else:
            raise NotImplementedError(f"Binary operation code {op_code} not implemented")

    def binary_subscr_op(self, instr: dis.Instruction) -> None:
        key = self.pop()
        container = self.pop()
        self.push(container[key])

    def store_subscr_op(self, instr: dis.Instruction) -> None:
        key = self.pop()
        container = self.pop()
        value = self.pop()
        container[key] = value

    def delete_subscr_op(self, instr: dis.Instruction) -> None:
        key = self.pop()
        container = self.pop()
        del container[key]

    def binary_slice_op(self, instr: dis.Instruction) -> None:
        end = self.pop()
        start = self.pop()
        container = self.pop()
        self.push(container[start:end])

    def store_slice_op(self, instr: dis.Instruction) -> None:
        end = self.pop()
        start = self.pop()
        container = self.pop()
        value = self.pop()
        container[start:end] = value

    def unary_positive_op(self, instr: dis.Instruction) -> None:
        self.push(+self.pop())

    def unary_negative_op(self, instr: dis.Instruction) -> None:
        self.push(-self.pop())

    def unary_not_op(self, instr: dis.Instruction) -> None:
        self.push(not self.pop())

    def unary_invert_op(self, instr: dis.Instruction) -> None:
        self.push(~self.pop())

    def compare_op_op(self, instr: dis.Instruction) -> None:
        oparg = instr.arg
        if oparg is None:
            raise ValueError("Compare operation requires arg")
        right = self.pop()
        left = self.pop()

        op_index = oparg >> 5
        force_bool = bool(oparg & 16)

        if op_index < len(dis.cmp_op):
            op_name = dis.cmp_op[op_index]
        else:
            raise NotImplementedError(f"Compare operation index {op_index} not implemented")

        ops = {
            '<': operator.lt,
            '<=': operator.le,
            '==': operator.eq,
            '!=': operator.ne,
            '>': operator.gt,
            '>=': operator.ge,
            'in': lambda a, b: a in b,
            'not in': lambda a, b: a not in b,
            'is': lambda a, b: a is b,
            'is not': lambda a, b: a is not b,
        }

        if op_name in ops:
            result = ops[op_name](left, right)
            if force_bool:
                result = bool(result)
            self.push(result)
        else:
            raise NotImplementedError(f"Compare operation {op_name} not implemented")

    def is_op_op(self, instr: dis.Instruction) -> None:
        invert = instr.argval
        right = self.pop()
        left = self.pop()
        result = left is right
        if invert:
            result = not result
        self.push(result)

    def contains_op_op(self, instr: dis.Instruction) -> None:
        invert = instr.argval
        right = self.pop()
        left = self.pop()
        result = left in right
        if invert:
            result = not result
        self.push(result)

    @staticmethod
    def jump_forward_op(instr: dis.Instruction) -> int:
        return instr.argval

    def jump_backward_op(self, instr: dis.Instruction) -> int:
        return instr.argval

    def pop_jump_if_true_op(self, instr: dis.Instruction) -> int | None:
        value = self.pop()
        if value:
            return instr.argval
        return None

    def pop_jump_if_false_op(self, instr: dis.Instruction) -> int | None:
        value = self.pop()
        if not value:
            return instr.argval
        return None

    def pop_jump_if_none_op(self, instr: dis.Instruction) -> int | None:
        value = self.pop()
        if value is None:
            return instr.argval
        return None

    def pop_jump_if_not_none_op(self, instr: dis.Instruction) -> int | None:
        value = self.pop()
        if value is not None:
            return instr.argval
        return None

    def to_bool_op(self, instr: dis.Instruction) -> None:
        self.push(bool(self.pop()))

    def get_iter_op(self, instr: dis.Instruction) -> None:
        self.push(iter(self.pop()))

    def for_iter_op(self, instr: dis.Instruction) -> int | None:
        iterator = self.top()
        try:
            value = next(iterator)
            self.push(value)
            return None
        except StopIteration:
            self.push(None)
            return instr.argval

    def end_for_op(self, instr: dis.Instruction) -> None:
        self.pop()

    def get_len_op(self, instr: dis.Instruction) -> None:
        self.push(len(self.top()))

    def call_op(self, instr: dis.Instruction) -> None:
        arg_count = instr.argval

        kwargs = {}
        if self.kw_names:
            num_kwargs = len(self.kw_names)
            num_pos = arg_count - num_kwargs

            all_args = self.popn(arg_count)
            args = all_args[:num_pos]
            kwargs = dict(zip(self.kw_names, all_args[num_pos:]))

            self.kw_names = None
        else:
            args = self.popn(arg_count)

        null_or_self = self.pop()
        func = self.pop()

        if null_or_self is not None:
            args = [null_or_self] + args

        self.push(func(*args, **kwargs))

    def make_function_op(self, instr: dis.Instruction) -> None:
        code = self.pop()

        def function(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            defaults = getattr(function, '__defaults__', None)
            kwdefaults = getattr(function, '__kwdefaults__', None)

            parsed_args = self._bind_arguments(code, args, kwargs, defaults, kwdefaults)

            f_locals = parsed_args
            frame = Frame(code, self.builtins, self.globals, f_locals)
            return frame.run()

        self.push(function)

    def _bind_arguments(
            self,
            code: types.CodeType,
            args: tuple[tp.Any, ...],
            kwargs: dict[str, tp.Any],
            defaults: tuple[tp.Any, ...] | None,
            kwdefaults: dict[str, tp.Any] | None
    ) -> dict[str, tp.Any]:
        result: dict[str, tp.Any] = {}
        varnames = code.co_varnames
        argcount = code.co_argcount
        kwonlyargcount = code.co_kwonlyargcount
        flags = code.co_flags

        has_varargs = bool(flags & CO_VARARGS)
        has_varkwargs = bool(flags & CO_VARKEYWORDS)

        for i in range(min(len(args), argcount)):
            result[varnames[i]] = args[i]

        for i in range(argcount):
            param_name = varnames[i]
            if param_name in kwargs:
                result[param_name] = kwargs.pop(param_name)

        if defaults:
            defaults_start = argcount - len(defaults)
            for i in range(len(defaults)):
                param_idx = defaults_start + i
                if varnames[param_idx] not in result:
                    result[varnames[param_idx]] = defaults[i]

        kwonly_start = argcount
        for i in range(kwonlyargcount):
            param_name = varnames[kwonly_start + i]
            if param_name in kwargs:
                result[param_name] = kwargs.pop(param_name)
            elif kwdefaults and param_name in kwdefaults:
                result[param_name] = kwdefaults[param_name]

        if has_varargs:
            varargs_idx = argcount + kwonlyargcount
            result[varnames[varargs_idx]] = args[argcount:]

        if has_varkwargs:
            varkwargs_idx = argcount + kwonlyargcount + (1 if has_varargs else 0)
            result[varnames[varkwargs_idx]] = kwargs

        return result

    def return_value_op(self, instr: dis.Instruction) -> bool:
        self.return_value = self.pop()
        return True

    def return_const_op(self, instr: dis.Instruction) -> bool:
        self.return_value = instr.argval
        return True

    def load_fast_load_fast_op(self, instr: dis.Instruction) -> None:
        oparg = instr.arg
        if oparg is None:
            raise ValueError("LOAD_FAST_LOAD_FAST requires arg")
        varnames = self.code.co_varnames
        idx1 = oparg >> 4
        idx2 = oparg & 15

        self.push(self.locals[varnames[idx1]])
        self.push(self.locals[varnames[idx2]])

    def load_fast_check_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        if name not in self.locals:
            raise UnboundLocalError(f"local variable '{name}' referenced before assignment")
        self.push(self.locals[name])

    def load_fast_and_clear_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        value = self.locals.get(name, None)
        self.push(value)
        if name in self.locals:
            del self.locals[name]

    def load_assertion_error_op(self, instr: dis.Instruction) -> None:
        self.push(AssertionError)

    def store_fast_load_fast_op(self, instr: dis.Instruction) -> None:
        oparg = instr.arg
        if oparg is None:
            raise ValueError("STORE_FAST_LOAD_FAST requires arg")
        varnames = self.code.co_varnames
        idx1 = oparg >> 4
        idx2 = oparg & 15

        self.locals[varnames[idx1]] = self.pop()
        self.push(self.locals[varnames[idx2]])

    def store_fast_store_fast_op(self, instr: dis.Instruction) -> None:
        oparg = instr.arg
        if oparg is None:
            raise ValueError("STORE_FAST_STORE_FAST requires arg")
        varnames = self.code.co_varnames
        idx1 = oparg >> 4
        idx2 = oparg & 15

        value2 = self.pop()
        value1 = self.pop()
        self.locals[varnames[idx1]] = value1
        self.locals[varnames[idx2]] = value2

    def load_attr_op(self, instr: dis.Instruction) -> None:
        obj = self.pop()
        attr = getattr(obj, instr.argval)
        self.push(attr)

        if instr.arg is not None and (instr.arg & 1):
            self.push(None)

    def store_attr_op(self, instr: dis.Instruction) -> None:
        value = self.pop()
        obj = self.pop()
        setattr(obj, instr.argval, value)

    def delete_attr_op(self, instr: dis.Instruction) -> None:
        obj = self.pop()
        delattr(obj, instr.argval)

    def call_kw_op(self, instr: dis.Instruction) -> None:
        arg_count = instr.argval
        kwargs_names = self.pop()

        all_args = self.popn(arg_count)

        num_kwargs = len(kwargs_names)
        num_pos = arg_count - num_kwargs

        args = all_args[:num_pos]
        kwargs = dict(zip(kwargs_names, all_args[num_pos:]))

        null_or_self = self.pop()
        func = self.pop()

        if null_or_self is not None:
            args = [null_or_self] + args

        self.push(func(*args, **kwargs))

    def call_intrinsic_1_op(self, instr: dis.Instruction) -> None:
        intrinsic = instr.argval
        arg = self.pop()

        if intrinsic == 1:
            print(arg)
            self.push(None)
        elif intrinsic == 2:
            module = arg
            if hasattr(module, '__all__'):
                names = module.__all__
            else:
                names = [name for name in dir(module) if not name.startswith('_')]
            for name in names:
                self.locals[name] = getattr(module, name)
            self.push(None)
        elif intrinsic == 3:
            if isinstance(arg, StopIteration):
                raise RuntimeError("generator raised StopIteration")
            self.push(arg)
        elif intrinsic == 5:
            self.push(+arg)
        elif intrinsic == 6:
            self.push(tuple(arg))
        else:
            raise NotImplementedError(f"Intrinsic {intrinsic} not implemented")

    def call_intrinsic_2_op(self, instr: dis.Instruction) -> None:
        intrinsic = instr.argval

        if intrinsic == 1:
            raise NotImplementedError("PREP_RERAISE_STAR intrinsic not implemented")
        elif intrinsic == 2:
            raise NotImplementedError("TYPEVAR intrinsic not implemented")
        else:
            raise NotImplementedError(f"Intrinsic {intrinsic} not implemented")

    def set_function_attribute_op(self, instr: dis.Instruction) -> None:
        attr = instr.argval
        func = self.pop()
        value = self.pop()

        if attr & 0x01:
            func.__defaults__ = value
        if attr & 0x02:
            func.__kwdefaults__ = value
        if attr & 0x04:
            func.__annotations__ = value
        if attr & 0x08:
            pass

        self.push(func)

    def format_simple_op(self, instr: dis.Instruction) -> None:
        value = self.pop()
        result = value.__format__("")
        self.push(result)

    def format_with_spec_op(self, instr: dis.Instruction) -> None:
        spec = self.pop()
        value = self.pop()
        self.push(format(value, spec))

    def convert_value_op(self, instr: dis.Instruction) -> None:
        conversion = instr.arg
        value = self.pop()

        if conversion == 1:
            self.push(str(value))
        elif conversion == 2:
            self.push(repr(value))
        elif conversion == 3:
            self.push(ascii(value))
        else:
            self.push(value)

    def raise_varargs_op(self, instr: dis.Instruction) -> None:
        argc = instr.argval

        if argc == 0:
            raise
        elif argc == 1:
            exc = self.pop()
            raise exc
        elif argc == 2:
            cause = self.pop()
            exc = self.pop()
            raise exc from cause
        else:
            raise NotImplementedError(f"RAISE_VARARGS with {argc} args not implemented")

    def reraise_op(self, instr: dis.Instruction) -> None:
        exc = self.pop()
        tb = self.pop()
        raise exc.with_traceback(tb)

    def pop_except_op(self, instr: dis.Instruction) -> None:
        self.pop()
        self.pop()

    def match_mapping_op(self, instr: dis.Instruction) -> None:
        obj = self.top()
        import collections.abc
        self.push(isinstance(obj, collections.abc.Mapping))

    def match_sequence_op(self, instr: dis.Instruction) -> None:
        obj = self.top()
        import collections.abc
        is_seq = isinstance(obj, collections.abc.Sequence) and not isinstance(obj, (str, bytes, bytearray))
        self.push(is_seq)

    def match_keys_op(self, instr: dis.Instruction) -> None:
        keys = self.pop()
        mapping = self.top()

        if all(key in mapping for key in keys):
            values = tuple(mapping[key] for key in keys)
            self.push(values)
            self.push(True)
        else:
            self.push(False)

    def jump_backward_no_interrupt_op(self, instr: dis.Instruction) -> int:
        return instr.argval

    def extended_arg_op(self, instr: dis.Instruction) -> None:
        pass

    def build_tuple_op(self, instr: dis.Instruction) -> None:
        count = instr.argval
        items = self.popn(count)
        self.push(tuple(items))

    def build_list_op(self, instr: dis.Instruction) -> None:
        count = instr.argval
        items = self.popn(count)
        self.push(items)

    def build_set_op(self, instr: dis.Instruction) -> None:
        count = instr.argval
        items = self.popn(count)
        self.push(set(items))

    def build_map_op(self, instr: dis.Instruction) -> None:
        count = instr.argval
        items = self.popn(2 * count)
        result = {}
        for i in range(0, len(items), 2):
            key = items[i]
            value = items[i + 1]
            result[key] = value
        self.push(result)

    def build_const_key_map_op(self, instr: dis.Instruction) -> None:
        count = instr.argval
        keys = self.pop()
        values = self.popn(count)
        self.push(dict(zip(keys, values)))

    def build_string_op(self, instr: dis.Instruction) -> None:
        count = instr.argval
        strings = self.popn(count)
        self.push(''.join(strings))

    def build_slice_op(self, instr: dis.Instruction) -> None:
        argc = instr.argval
        if argc == 2:
            stop = self.pop()
            start = self.pop()
            self.push(slice(start, stop))
        elif argc == 3:
            step = self.pop()
            stop = self.pop()
            start = self.pop()
            self.push(slice(start, stop, step))
        else:
            raise NotImplementedError(f"BUILD_SLICE with {argc} args not implemented")

    def list_append_op(self, instr: dis.Instruction) -> None:
        value = self.pop()
        list_obj = self.data_stack[-instr.argval]
        list_obj.append(value)

    def list_extend_op(self, instr: dis.Instruction) -> None:
        iterable = self.pop()
        list_obj = self.data_stack[-instr.argval]
        list_obj.extend(iterable)

    def set_add_op(self, instr: dis.Instruction) -> None:
        value = self.pop()
        set_obj = self.data_stack[-instr.argval]
        set_obj.add(value)

    def set_update_op(self, instr: dis.Instruction) -> None:
        iterable = self.pop()
        set_obj = self.data_stack[-instr.argval]
        set_obj.update(iterable)

    def map_add_op(self, instr: dis.Instruction) -> None:
        value = self.pop()
        key = self.pop()
        dict_obj = self.data_stack[-instr.argval]
        dict_obj[key] = value

    def dict_update_op(self, instr: dis.Instruction) -> None:
        updates = self.pop()
        dict_obj = self.data_stack[-instr.argval]
        dict_obj.update(updates)

    def dict_merge_op(self, instr: dis.Instruction) -> None:
        updates = self.pop()
        dict_obj = self.data_stack[-instr.argval]
        for key, value in updates.items():
            if key in dict_obj:
                raise KeyError(f"duplicate key: {key!r}")
            dict_obj[key] = value

    def unpack_sequence_op(self, instr: dis.Instruction) -> None:
        count = instr.argval
        sequence = self.pop()
        items = list(sequence)
        if len(items) != count:
            raise ValueError(f"not enough values to unpack (expected {count}, got {len(items)})")
        for item in reversed(items):
            self.push(item)

    def unpack_ex_op(self, instr: dis.Instruction) -> None:
        counts = instr.argval
        before = counts & 0xFF
        after = (counts >> 8) & 0xFF

        sequence = self.pop()
        items = list(sequence)

        if len(items) < before + after:
            raise ValueError("not enough values to unpack")

        middle = items[before:len(items) - after] if after > 0 else items[before:]

        for i in range(after - 1, -1, -1):
            self.push(items[len(items) - after + i])

        self.push(middle)

        for i in range(before - 1, -1, -1):
            self.push(items[i])

    def call_function_ex_op(self, instr: dis.Instruction) -> None:
        flags = instr.argval

        kwargs = {}
        if flags & 0x01:
            kwargs = self.pop()

        args = self.pop()

        null_or_self = self.pop()
        func = self.pop()

        if null_or_self is not None:
            args = (null_or_self,) + tuple(args)

        self.push(func(*args, **kwargs))

    def kw_names_op(self, instr: dis.Instruction) -> None:
        self.kw_names = instr.argval

    def import_name_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        fromlist = self.pop()
        level = self.pop()
        module = __import__(name, self.globals, self.locals, fromlist, level)
        self.push(module)

    def import_from_op(self, instr: dis.Instruction) -> None:
        name = instr.argval
        module = self.top()
        self.push(getattr(module, name))

    def check_exc_match_op(self, instr: dis.Instruction) -> None:
        exc_type = self.pop()
        exc = self.pop()

        if isinstance(exc_type, tuple):
            result = isinstance(exc, exc_type)
        else:
            result = isinstance(exc, exc_type)

        self.push(exc)
        self.push(result)

    def push_exc_info_op(self, instr: dis.Instruction) -> None:
        import sys
        exc_info = sys.exc_info()
        if exc_info[0] is not None:
            self.push(exc_info[1])
        else:
            self.push(None)

    def check_eg_match_op(self, instr: dis.Instruction) -> None:
        exc = self.pop()

        self.push(exc)
        self.push(False)


class VirtualMachine:
    def run(self, code_obj: types.CodeType) -> None:
        """
        :param code_obj: code for interpreting
        """
        globals_context: dict[str, tp.Any] = {}
        frame = Frame(code_obj, builtins.globals()['__builtins__'], globals_context, globals_context)
        return frame.run()
