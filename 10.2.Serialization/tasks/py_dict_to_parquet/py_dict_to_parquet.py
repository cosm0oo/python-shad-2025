import pyarrow as pa
import pyarrow.parquet as pq


ValueType = int | list[int] | str | dict[str, str]


def save_rows_to_parquet(rows: list[dict[str, ValueType]], output_filepath: str) -> None:
    """
    Save rows to parquet file.

    :param rows: list of rows containing data.
    :param output_filepath: local filepath for the resulting parquet file.
    :return: None.
    """
    if not rows:
        schema = pa.schema([])
        table = pa.table([], schema=schema)
        pq.write_table(table, output_filepath)
        return

    field_order = []
    field_types = {}
    field_present = {}

    def get_pa_type(value: ValueType) -> pa.DataType:
        if isinstance(value, int):
            return pa.int64()
        elif isinstance(value, list):
            return pa.list_(pa.int64())
        elif isinstance(value, str):
            return pa.string()
        elif isinstance(value, dict):
            return pa.map_(pa.string(), pa.string())

    for row_idx, row in enumerate(rows):
        for key, value in row.items():
            if key not in field_order:
                field_order.append(key)
                field_present[key] = set()

            field_present[key].add(row_idx)

            pa_type = get_pa_type(value)
            if key in field_types:
                if field_types[key] != pa_type:
                    raise TypeError(f"Field {key} has different types")
            else:
                field_types[key] = pa_type

    all_row_indices = set(range(len(rows)))
    fields = []
    for key in field_order:
        nullable = field_present[key] != all_row_indices
        fields.append(pa.field(key, field_types[key], nullable=nullable))

    schema = pa.schema(fields)

    table_data = []
    for row in rows:
        row_data = {}
        for key in field_order:
            if key in row:
                row_data[key] = row[key]
            else:
                row_data[key] = None
        table_data.append(row_data)

    table = pa.Table.from_pylist(table_data, schema=schema)
    pq.write_table(table, output_filepath)
