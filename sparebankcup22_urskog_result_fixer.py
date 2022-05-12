import argparse
import ftplib
import logging
import os
import time
import xml.etree.ElementTree


def check_files_are_valid(input_filepath, output_filepath):
    # Cannot write to the input file, that would cause an infinite loop of updates!
    assert not os.path.abspath(input_filepath) == os.path.abspath(output_filepath), \
        "The input and output files cannot be the same. Write the output to another directory!"

    # Check that files have xml-extension.
    assert os.path.splitext(input_filepath)[-1].casefold() == '.xml'.casefold(), "Input must be an xml-file"
    assert os.path.splitext(output_filepath)[-1].casefold() == '.xml'.casefold(), "Output must be an xml-file"

    # Create directory for output if it does not exist.
    output_dir = os.path.dirname(output_filepath)
    if not os.path.exists(output_dir):
        logging.info(f"Output directory does not exist. Making '{output_dir}'")
        os.mkdir(output_dir)


class SimpleFileMonitor:
    """Naively simple file monitor based on simple polling to avoid other dependencies."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.prev_last_modified = self.last_modified()

    def last_modified(self):
        return os.stat(self.filepath).st_mtime

    def was_modified_since_last(self):
        curr_last_modified = self.last_modified()

        if curr_last_modified != self.prev_last_modified:
            self.prev_last_modified = curr_last_modified
            return True

        return False


def fix_results(infile, outfile):
    # Read XML-file.
    tree = xml.etree.ElementTree.parse(infile)
    competition = tree.getroot()

    num_results_changed = 0

    for result in competition:
        # 5th series should be 25-shot sum 'BA_1To4'.
        series_sum_25 = result[0][5]
        assert series_sum_25.get('id') == 'BA_1To4', "Hmm, the assumption that 25-shot sum was the 5th series failed"

        # Extract 25-shot data if it exists.
        sum_25 = series_sum_25.get('sum')
        if sum_25 == '':
            continue
        it_25 = series_sum_25.get('it')

        # 8th series should be final total 'BA_tot'.
        series_tot = result[0][8]
        assert series_tot.get('id') == 'BA_tot', "Hmm, the assumption that the total was the 8th series failed"

        # Update total to be 25-shot sum.
        series_tot.set('sum', sum_25)
        series_tot.set('it', it_25)

        num_results_changed += 1
    logging.info(f"Fixed {num_results_changed} results")

    tree.write(outfile, encoding='UTF-8', xml_declaration=True)
    logging.info(f"Wrote fixed results to '{outfile}'")


def upload_fix_to_ftp_server(filepath, user, password):
    server = 'ftp.livevisning.com'
    logging.info(f"Uploading fixed result to '{server}'")

    ftp_session = ftplib.FTP(server)

    response = ftp_session.login(user=user, passwd=password)
    logging.info(f"FTP: {response.encode('unicode_escape')}")

    response = ftp_session.cwd('Sparebankcupen/Rapporter/Urskog')
    logging.info(f"FTP: {response.encode('unicode_escape')}")

    with open(filepath, 'rb') as file:
        filename = os.path.basename(filepath)
        response = ftp_session.storbinary(f'STOR {filename}', file)
        logging.info(f"FTP: {response.encode('unicode_escape')}")

    response = ftp_session.quit()
    logging.info(f"FTP: {response.encode('unicode_escape')}")


def sparebankcup22_urskog_result_fixer(input_filepath, output_filepath, ftp_user, ftp_password):
    try:
        use_ftp = ftp_user is not None
        if use_ftp:
            logging.info("FTP user is provided, will upload fix to server.")
        else:
            logging.info("FTP user is not provided. Will only write fix locally")

        check_files_are_valid(input_filepath, output_filepath)
        file_monitor = SimpleFileMonitor(input_filepath)
        logging.info(f"Monitoring '{input_filepath}' for changes")

        while True:
            if file_monitor.was_modified_since_last():
                logging.info("File has been updated, running fix!")
                fix_results(input_filepath, output_filepath)

                if use_ftp:
                    upload_fix_to_ftp_server(output_filepath, ftp_user, ftp_password)

            # We check file every second.
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("User pressed Ctrl-c")

    except BaseException as err:
        logging.error(err)

    logging.info("Shutting down...")


if __name__ == "__main__":
    # Setup logging to terminal.
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Setup arguments.
    parser = argparse.ArgumentParser(description="Bypasses a bug in the result compilation for Sparebankcupen 2022",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', type=str, help="Path to the input xml file.")
    parser.add_argument('output', type=str, help="Path to the output xml file (cannot be the same as input).")
    parser.add_argument('--ftp_user', type=str, default=None,
                        help="Username for 'ftp.livevisning.com' - will not use FTP if None.")
    parser.add_argument('--ftp_pass', type=str, default='',
                        help="Password for 'ftp.livevisning.com.'")

    # Parse arguments.
    args = parser.parse_args()

    # Start program.
    sparebankcup22_urskog_result_fixer(args.input, args.output, args.ftp_user, args.ftp_pass)
