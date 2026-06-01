import gzip
import shutil


def extract_gzip_file(
    gzip_path,
    output_path
):

    with gzip.open(
        gzip_path,
        "rb"
    ) as f_in:

        with open(
            output_path,
            "wb"
        ) as f_out:

            shutil.copyfileobj(
                f_in,
                f_out
            )

    return output_path
