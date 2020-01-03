# encoding: utf-8
# Wellcome Trust Sanger Institute
# Copyright (C) 2013  Wellcome Trust Sanger Institute
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os
import shutil
import subprocess
import re


class VerbosePrinter:
    """Class printing messages if verbose argument is set"""

    def __init__(self, verbose: bool, separator: str):
        """Constructor"""
        self.verbose = verbose
        self.sep = separator

    def is_verbose(self):
        return self.verbose

    def separator(self):
        """Get separator"""
        return self.sep

    def make_verbose(self, verbose=True):
        """Set verbosity"""
        self.verbose = verbose

    def set_separator(self, separator: str):
        """Set separator"""
        self.sep = separator

    def print(self, message):
        """Prints a message if set to verbose. If the message is a list, the method prints all elements,
        separated by the set separator"""
        if self.verbose:
            if isinstance(message, list):
                print(*message, sep=self.sep)
            else:
                print(message)


def which(program: str):
    """Checks if a given program exists on the system. Works analogously to the UNIX "which" function"""
    program_and_parameters = program.split(" ")
    if len(program_and_parameters) > 1:
        program = program_and_parameters[0]

    fpath, fname = os.path.split(program)
    if fpath:
        if is_executable(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_executable(exe_file):
                return exe_file
    return None


def is_executable(fpath: str):
    """Checks if a given path corresponds to an executable file"""
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def choose_executable(list_of_executables: list):
    """Chooses an executable from a list"""
    for executable in list_of_executables:
        if which(executable) is not None:
            return executable
    return None


def choose_executable_based_on_processor(list_of_executables: list):
    """Chooses an executable from a list and thereby takes into account processor features"""
    flags = []
    cpu_info = False
    if os.path.exists('/proc/cpuinfo'):
        cpu_info = True
        output = subprocess.Popen('grep flags /proc/cpuinfo', stdout=subprocess.PIPE,
                                  shell=True).communicate()[0].decode("utf-8")
        flags = output.split()

    for executable in list_of_executables:
        if cpu_info:
            if 'AVX2' in executable and 'avx2' not in flags:
                continue
            elif 'AVX' in executable and 'avx' not in flags:
                continue
            elif 'SSE3' in executable and 'ssse3' not in flags:
                continue

        if which(executable) is not None:
            return executable

    return None


def replace_executable(command, alternative_executable):
    """Changes the executable in a command"""
    executable_and_params = command.split(" ")
    executable_and_params[0] = alternative_executable
    return " ".join(executable_and_params)


def do_files_exist(directory, basenames, suffix_regex, verbose=False):
    """Checks if files with a given name structure exist"""
    files = os.listdir(directory)
    for file in files:
        full_path = os.path.join(directory, file)
        for basename in basenames:
            regex = "^" + basename + suffix_regex
            if re.match(regex, file) is not None and os.path.exists(full_path):
                if verbose:
                    print("File exists: " + full_path)
                return True
    return False


def delete_files(directory, basenames, suffix_regex, verbose=False):
    """Deletes files with a given name structure"""
    files = os.listdir(directory)
    for file in files:
        full_path = os.path.join(directory, file)
        for basename in basenames:
            regex = "^" + basename + suffix_regex
            if re.match(regex, file) is not None and os.path.exists(full_path):
                if verbose:
                    print("Deleting file: " + full_path)
                os.remove(full_path)


def rename_files(input_to_output_filenames):
    """Renames files"""
    for input_file, output_file in input_to_output_filenames.items():
        if os.path.exists(input_file):
            shutil.move(input_file, output_file)
