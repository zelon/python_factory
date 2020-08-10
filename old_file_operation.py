# tested on python2.7

import argparse
import glob
import os
import shutil
import stat
import sys
import time

import extractDatetime

class OldFileCollector:
    def __init__(self, target_directory, old_days, keep_count):
        self.target_directory = target_directory
        self.old_days = old_days
        self.keep_count = keep_count

    @staticmethod
    def sort_tuple_by_first(tuple_unit):
        return int(tuple_unit[0])

    def get_filelist(self):
        search_pattern = self.target_directory + r"\*"
        print("SearchPattern:" + search_pattern)
        return glob.glob(search_pattern)

    @staticmethod
    def attach_elapsed_time_to_filelist(filelist):
        current_time_seconds = int(time.time())

        filelist_with_elapsed_time = []
        for filename in filelist:
            file_creation_time_second = int(os.path.getmtime(filename))
            elapsed_time_second = current_time_seconds - file_creation_time_second
            filelist_with_elapsed_time.append((elapsed_time_second, filename))

        return filelist_with_elapsed_time

    def filter_old(self, filelist_with_elapsed_time):
        old_seconds = 60*60*24*self.old_days

        old_filelist = []
        for elapsed_time_second, filename in filelist_with_elapsed_time:
            if elapsed_time_second > old_seconds:
                print("Found old: %s is %d seconds old" % (filename, elapsed_time_second))
                old_filelist.append(filename)

        return old_filelist

    def remove_keep_count(self, filelist):
        sorted_list = sorted(filelist, key=OldFileCollector.sort_tuple_by_first)
        return sorted_list[self.keep_count:]

    @staticmethod
    def on_remove_error(_, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)

        if os.path.exists(path):
            print("Cannot remove %s" % path)

    def collect(self):
        files = self.get_filelist()
        print("collected count:%d" % len(files))
        filelist_with_elapsed_time = OldFileCollector.attach_elapsed_time_to_filelist(files)
        filelist_with_elapsed_time.sort(key=OldFileCollector.sort_tuple_by_first)
        target_filelist = self.remove_keep_count(filelist_with_elapsed_time)
        print("target count:%d" % len(target_filelist))
        target_filename_list = self.filter_old(target_filelist)
        print("old count:%d" % len(target_filename_list))

        return target_filename_list


class Lister:
    def __init__(self):
        pass

    def do(self, target_filename_list):
        for filename in target_filename_list:
            print(filename)


class Deleter:
    def __init__(self):
        pass

    def remove(self, filename):
        if not os.path.exists(filename):
            print("Cannot find file:%s" % filename)
            return

        print("Delete %s" % filename)

        if os.path.isdir(filename):
            shutil.rmtree(filename, ignore_errors=False, onerror=OldFileCollector.on_remove_error)
        else:
            os.chmod(filename, stat.S_IWRITE)
            os.remove(filename)

    def do(self, target_filename_list):
        for filename in target_filename_list:
            self.remove(filename)


class Mover:
    def __init__(self, destination_directory):
        self.destination_parent_directory = destination_directory

    def convert_time_to_string(self, stime):
        return '{0}-{1:02}-{2:02}'.format(stime.tm_year, stime.tm_mon, stime.tm_mday)

    def get_sub_directory_name(self, filename):
        _, only_filename = os.path.split(filename)
        try:
            year, month, day = extractDatetime.extract_datetime(only_filename)
            return '{0}-{1}-{2}'.format(year, month, day)
        except:
            file_creation_time = time.localtime(os.path.getmtime(filename))
            return self.convert_time_to_string(file_creation_time)
            

    def do(self, target_filename_list):
        for filename in target_filename_list:
            sub_directory_name = self.get_sub_directory_name(filename)

            destination_directory = os.path.join(self.destination_parent_directory, sub_directory_name)
            if os.path.exists(destination_directory) == False:
                os.makedirs(destination_directory)
            _, source_file_name = os.path.split(filename)
            destination_path = os.path.join(destination_directory, source_file_name)

            print("move from: {0} to: {1}".format(filename, destination_path))
            
            shutil.move(filename, destination_path)


def print_usage():
    print("usage: %s directory old_days keep_count [delete|move] [move_destination_directory]" % os.path.basename(sys.argv[0]))

def main():
    command_parser = argparse.ArgumentParser(description="find old files and operate")

    command_parser.add_argument('--check_directory', default='.', help='check directory')
    command_parser.add_argument('--before_days', type=int, default=30, help='target days to be old')
    command_parser.add_argument('--min_keep_count', type=int, default=30, help='minimum keep count')
    command_parser.add_argument('--exclude', nargs='*', help='exclude name')
    command_parser.add_argument('--move_destination_directory', help='move destination directory')
    command_parser.add_argument('command', choices=['list', 'delete', 'move'])

    args = command_parser.parse_args()

    check_directory = args.check_directory
    old_days = args.before_days
    keep_count = args.min_keep_count
    exclude_names = args.exclude
    move_destination_directory = args.move_destination_directory
    operation_type = args.command

    if operation_type == "move" and move_destination_directory is None:
        command_parser.print_help()
        return

    print("Check directory: " + check_directory)
    print("Old days: " + str(old_days))
    print("Keep count: " + str(keep_count))
    print("OperationType: " + operation_type)
    for exclude_name in exclude_names:
        print("exclude_name: " + exclude_name)
    if operation_type == "move":
        print("MoveDestinationDirectory: " + move_destination_directory)

    if not os.path.exists(check_directory):
        print("not exist directory: " + check_directory)
        return

    if old_days < 0:
        print("old_days is less than 0.old_days: {0}".format(old_days))
        return

    if keep_count < 0:
        print("keep_count is less than zero,keep_count: {0}".format(keep_count))
        return

    old_file_collector = OldFileCollector(check_directory, old_days, keep_count)
    target_filenames = old_file_collector.collect()
    operator = None
    if operation_type == "delete":
        operator = Deleter()
    elif operation_type == "move":
        operator = Mover(move_destination_directory)
    elif operation_type == "list":
        operator = Lister()
    else:
        print("operation type error")
        return

    operator.do(target_filenames)

if __name__ == "__main__":
    main()
