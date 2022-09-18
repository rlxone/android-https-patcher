import sys
import os
import subprocess
import shutil
import platform
import traceback
from xml.dom import minidom

# Messages

class ErrorMessages:
    OUTPUT_FILENAME_EXISTS_MESSAGE = 'Output filename exists.\nDo you want to overwrite this file? [Y/n]'
    ABORT_MESSAGE = 'Abort'
    INVALID_ARGUMENTS_MESSAGE = 'Invalid arguments'
    SCRIPT_USAGE_MESSAGE = 'Usage: python apk_rebuild.py -i filename.apk -o output.apk'
    INPUT_FILENAME_NOT_EXISTS_MESSAGE = 'Input filename not exists'
    INVALID_OS_MESSAGE = 'Please use macOS or Windows'

class ProgressMessages:
    @staticmethod
    def message_unpacking(first, second):
        return f'Unpacking {first} to {second}...'

    @staticmethod
    def message_change_manifest(first):
        return f'Change manifest {first}...'
    
    @staticmethod
    def message_create_resources(first):
        return f'Create resources {first}...'

    @staticmethod
    def message_building(first, second):
        return f'Building {first} from {second}...'

    @staticmethod
    def message_zipalign(first, second):
        return f'Zipalign {first} to {second}...'

    @staticmethod
    def message_remove_file(first):
        return f'Remove file {first}...'

    @staticmethod
    def message_remove_folder(first):
        return f'Remove folder {first}...'

    @staticmethod
    def message_rename_file(first, second):
        return f'Rename file from {first} to {second}...'

    @staticmethod
    def message_keystore(first):
        return f'Obtaining keystore from {first}...'

    @staticmethod
    def message_sign(first):
        return f'Sign {first}...'

    @staticmethod
    def message_rebuild_completed():
        return f'Rebuild completed!'

# LOGGER

class Logger:
    class Colors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    @staticmethod
    def success(string):
        print(f"{Logger.Colors.OKGREEN}{string}{Logger.Colors.ENDC}")
    
    @staticmethod
    def info(string):
        print(f"{Logger.Colors.OKCYAN}{string}{Logger.Colors.ENDC}")

    @staticmethod
    def warning(string):
        print(f"{Logger.Colors.WARNING}{string}{Logger.Colors.ENDC}")

    @staticmethod
    def error(string):
        print(f"{Logger.Colors.FAIL}{string}{Logger.Colors.ENDC}")

# UTILS

class Utils:
    class Constants:
        PLATFORM_WINDOWS = 'Windows'
        PLATFORM_MACOS = 'Darwin'

    def write_to_file(self, filename, content):
        with open(filename,'w') as f:
            f.write(content)

    def makedirs(self, filename):
        dirname = os.path.dirname(filename)
        os.makedirs(dirname, exist_ok=True)

    def file_exists(self, filename):
        return os.path.isfile(filename)

    def remove_file(self, filename):
        os.remove(filename)

    def rename_file(self, filename_from, filename_to):
        os.rename(filename_from, filename_to)

    def remove_dir(self, folder):
        shutil.rmtree(folder, ignore_errors=True)

    def check_os(self):
        self.is_os_windows() or self.is_os_macos()

    def is_os_windows(self):
        return platform.system() == Utils.Constants.PLATFORM_WINDOWS

    def is_os_macos(self):
        return platform.system() == Utils.Constants.PLATFORM_MACOS

# PARSER

class Parser:
    class Constants:
        ARGUMENTS_COUNT = 5
        INPUT_FILENAME_ARG = '-i'
        OUTPUT_FILENAME_ARG = '-o'
        SUCCESS_DECISION = 'Y'

    __utils = Utils()

    def get_args(self, args):
        if self.__utils.check_os():
            raise Exception(ErrorMessages.INVALID_OS_MESSAGE)
        if len(args) == Parser.Constants.ARGUMENTS_COUNT:
            if args[1] == Parser.Constants.INPUT_FILENAME_ARG and args[3] == Parser.Constants.OUTPUT_FILENAME_ARG:
                return [args[2], args[4]]
            else:
                raise Exception(f'{ErrorMessages.INVALID_ARGUMENTS_MESSAGE}\n{ErrorMessages.SCRIPT_USAGE_MESSAGE}')
        else:
            raise Exception(f'{ErrorMessages.INVALID_ARGUMENTS_MESSAGE}\n{ErrorMessages.SCRIPT_USAGE_MESSAGE}')

    def process_args(self, input_filename, output_filename):
        if self.__utils.file_exists(input_filename):
            should_rewrite_output = True
            if self.__utils.file_exists(output_filename):
                Logger.info(f'{ErrorMessages.OUTPUT_FILENAME_EXISTS_MESSAGE}')
                decision = input()
                should_rewrite_output = decision == Parser.Constants.SUCCESS_DECISION
            if not should_rewrite_output:
                raise Exception(f'{ErrorMessages.ABORT_MESSAGE}')
        else:
            raise Exception(f'{ErrorMessages.INPUT_FILENAME_NOT_EXISTS_MESSAGE}')

# REBUILDER

class Rebuilder:
    class Constants:
        KEYSTORE_FILENAME = 'my.keystore'
        NETWORK_SECURITY_XML = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
    <debug-overrides>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
"""

    __utils = Utils()

    def rebuild_apk(self, input_filename, output_filename):
        unpacked_folder = f'{input_filename}_unpacked'
        manifest_filename = f'{unpacked_folder}/AndroidManifest.xml'
        network_security_xml = f'{unpacked_folder}/res/xml/network_security_config.xml'
        aligned_filename = f'{output_filename}_aligned'
        Logger.success(ProgressMessages.message_unpacking(input_filename, unpacked_folder))
        self.__unpack_apk(input_filename, unpacked_folder)
        Logger.success(ProgressMessages.message_change_manifest(manifest_filename))
        self.__change_manifest(manifest_filename)
        Logger.success(ProgressMessages.message_create_resources(network_security_xml))
        self.__create_network_security_xml(network_security_xml, Rebuilder.Constants.NETWORK_SECURITY_XML)
        Logger.success(ProgressMessages.message_building(output_filename, unpacked_folder))
        self.__build_apk(output_filename, unpacked_folder)
        Logger.success(ProgressMessages.message_zipalign(output_filename, aligned_filename))
        self.__zipalign_apk(output_filename, aligned_filename)
        Logger.success(ProgressMessages.message_remove_file(output_filename))
        self.__utils.remove_file(output_filename)
        Logger.success(ProgressMessages.message_remove_folder(unpacked_folder))
        self.__utils.remove_dir(unpacked_folder)
        Logger.success(ProgressMessages.message_rename_file(aligned_filename, output_filename))
        self.__utils.rename_file(aligned_filename, output_filename)
        Logger.success(ProgressMessages.message_keystore(Rebuilder.Constants.KEYSTORE_FILENAME))
        self.__create_keystore_if_needed(Rebuilder.Constants.KEYSTORE_FILENAME)
        Logger.success(ProgressMessages.message_sign(output_filename))
        self.__sign_apk(output_filename, Rebuilder.Constants.KEYSTORE_FILENAME)
        Logger.success(ProgressMessages.message_rebuild_completed())

    def __change_manifest(self, manifest_filename):
        xmldoc = minidom.parse(manifest_filename)
        application_item = xmldoc.getElementsByTagName("application")
        application_item[0].setAttribute("android:networkSecurityConfig", "@xml/network_security_config")
        application_item[0].setAttribute('android:extractNativeLibs', 'true')
        application_item[0].setAttribute('android:usesCleartextTraffic', 'true')
        self.__utils.write_to_file(manifest_filename, xmldoc.toxml())

    def __unpack_apk(self, input_filename, folder):
        shell = self.__utils.is_os_windows()
        subprocess.call(["apktool", "d", input_filename, "-f", "-o", folder], shell=shell)

    def __build_apk(self, output_filename, folder):
        shell = self.__utils.is_os_windows()
        subprocess.call(["apktool", "b", folder, '--use-aapt2', "-o", output_filename], shell=shell)

    def __zipalign_apk(self, filename, output_filename):
        zipalign_path = self.__get_zipalign_path()
        shell = self.__utils.is_os_windows()
        subprocess.call([zipalign_path, '-f', '-v', '4', filename, output_filename], shell=shell)

    def __sign_apk(self, filename, keystore_filename):
        apksigner_path = self.__get_apksigner_path()
        shell = self.__utils.is_os_windows()
        subprocess.call([apksigner_path, 'sign', '--ks', keystore_filename, filename], shell=shell)

    def __create_keystore_if_needed(self, filename):
        if not self.__utils.file_exists(filename):
            keytool = None
            shell = None
            if self.__utils.is_os_windows():
                command = 'where /r "%programfiles(x86)%\Java" keytool.exe'
                sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                keytool = sp.communicate()[0].decode('utf-8').strip('\n')
                shell = True
            else:
                keytool = 'keytool'
                shell = False
            subprocess.call([keytool, '-genkey', '-v', '-keystore', filename, '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000'], shell=shell)

    def __create_network_security_xml(self, filename, content):
        self.__utils.makedirs(filename)
        self.__utils.write_to_file(filename, content)

    def __get_zipalign_path(self):
        command = None
        if self.__utils.is_os_windows():
            command = 'where /r %LocalAppData%\Android zipalign.exe'
        elif self.__utils.is_os_macos():
            command = 'find ~/Library/Android/sdk/build-tools -name zipalign'
        else:
            command = 'find ~/Android/Sdk/build-tools -name zipalign'
        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return sp.communicate()[0].decode('utf-8').split('\n')[0]

    def __get_apksigner_path(self):
        command = None
        if self.__utils.is_os_windows():
            command = 'where /r "%LocalAppData%\Android" apksigner.bat'
        elif self.__utils.is_os_macos():
            command = 'find ~/Library/Android/sdk/build-tools -name apksigner'
        else:
            command = 'find ~/Android/Sdk/build-tools -name apksigner'
        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return sp.communicate()[0].decode('utf-8').split('\n')[0]

# MAIN

def main():
    parser = Parser()
    rebuilder = Rebuilder()
    try:
        filenames = parser.get_args(sys.argv)
        input_filename = filenames[0]
        output_filename = filenames[1]
        parser.process_args(input_filename, output_filename)
        rebuilder.rebuild_apk(input_filename, output_filename)
    except Exception as exception:
        Logger.error(exception)
        traceback.print_tb(exception.__traceback__)

if __name__ == "__main__":
    main()
