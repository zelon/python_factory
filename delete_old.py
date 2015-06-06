# tested on python2.7

import glob
import os
import shutil
import time
from types import *

class DeleteOld:
    def __init__(self, target_directory, old_days, keep_count):
        assert(isinstance(target_directory, StringType))
        assert(isinstance(old_days, IntType))
        assert(isinstance(keep_count, IntType))

        self.target_directory = target_directory
        self.old_days = old_days
        self.keep_count = keep_count

    @staticmethod
    def sort_tuple_by_first(tuple_unit):
        assert(isinstance(tuple_unit, TupleType))
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
            file_modified_time_second = int(os.path.getmtime(filename))
            elapsed_time_second = current_time_seconds - file_modified_time_second
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
        sorted_list = sorted(filelist, key=DeleteOld.sort_tuple_by_first)
        return sorted_list[self.keep_count:]

    @staticmethod
    def remove(filename):
        if not os.path.exists(filename):
            print("Cannot find file:%s" % filename)
            return

        print("Delete %s" % filename)

        if os.path.isdir(filename):
            shutil.rmtree(filename, ignore_errors=True, onerror=DeleteOld.on_remove_error)
        else:
            os.remove(filename)

    @staticmethod
    def on_remove_error(_, path):
        print("Cannot remove %s" % path)

    def do(self):
        files = self.get_filelist()
        filelist_with_elapsed_time = DeleteOld.attach_elapsed_time_to_filelist(files)
        filelist_with_elapsed_time.sort(key=DeleteOld.sort_tuple_by_first)
        target_filelist = self.remove_keep_count(filelist_with_elapsed_time)
        print("target count:%d" % len(target_filelist))
        target_filename_list = self.filter_old(target_filelist)
        print("old count:%d" % len(target_filename_list))

        for filename in target_filename_list:
            DeleteOld.remove(filename)

def print_usage():
    print("usage: %s directory old_days keep_count" % os.path.basename(sys.argv[0]))

def main():
    import sys

    if len(sys.argv) != 4:
        print_usage()
        return

    target_directory = os.path.abspath(sys.argv[1])
    old_days = int(sys.argv[2])
    keep_count = int(sys.argv[3])

    print("Target directory: " + target_directory)
    print("Old days: " + str(old_days))
    print("Keep count: " + str(keep_count))

    if not os.path.exists(target_directory):
        print("not exist directory")
        return

    if old_days < 0:
        print("old_days is less than 0")
        return

    if keep_count < 0:
        print("keep_count is less than zero")
        return

    delete_old = DeleteOld(target_directory, old_days, keep_count)
    delete_old.do()

if __name__ == "__main__":
    main()
