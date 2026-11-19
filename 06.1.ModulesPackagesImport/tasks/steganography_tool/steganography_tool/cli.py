import click
from steganography_tool.encode import encode_message
from steganography_tool.decode import decode_message
from steganography_tool.utils import get_base_file, write_file, read_file


@click.group()
def cli():
    pass


@cli.command()
@click.argument('output_filename')
@click.argument('secret_message')
def encode(output_filename, secret_message):
    base_data = get_base_file()
    encoded_data = encode_message(base_data, secret_message)
    write_file(encoded_data, output_filename)


@cli.command()
@click.argument('input_filename')
def decode(input_filename):
    data = read_file(input_filename)
    message = decode_message(data)
    print(message)


if __name__ == '__main__':
    cli()
