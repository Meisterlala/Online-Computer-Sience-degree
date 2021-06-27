#!/usr/bin/env python
import os
import sys
from concurrent.futures import ProcessPoolExecutor, wait
from typing import List

from colorama import Fore, init

import VMFile


def main():
    # init colorama Color output
    init()

    # Handle arguments
    files = ArgumentsParse()
    print("Translating:")
    for file in files:
        print(f"\t{file}")

    # Read Files
    VMFiles = VMFile.FilenamesToObjects(files)

    # Parse Files Multi threaded
    FilePool = ProcessPoolExecutor()
    FileFutures = []
    for VMObject in VMFiles:
        FileFutures.append(FilePool.submit(VMObject.Parse))
    wait(FileFutures)

    # Translate Files Multi threaded
    TranslatePool = ProcessPoolExecutor()
    TranslateFutures = []
    for VMObject in VMFiles:
        TranslateFutures.append(TranslatePool.submit(VMObject.Translate))
    wait(TranslateFutures)

    # Combine Outputs
    translated = BootstrapCode()
    for VMObject in VMFiles:
        translated.extend(VMObject.assembly)

    # Write output
    outFilename = os.path.basename(sys.argv[1]) + ".asm"
    print(f"Writing {outFilename}")
    out = open(outFilename, "w")
    out.write(OutputString(translated, outFilename))
    out.close()

    sys.exit(0)


def OutputString(lines: List[str], filename):
    # Header
    outp = f"// Generated from {filename}"

    for outLine in lines:
        # Indent if not a label
        if outLine[0] == "(":  # label
            outp += "\r\n"
        elif outLine[0] == "/":
            outp += "\r\n\r\n\t"
        else:    # Code
            outp += "\r\n\t"
        outp += outLine
    return outp


def ArgumentsParse():
    if len(sys.argv) != 2:
        print("Usage: VMTranslator.py (Filename|Directory))")
        print(f"Given: {str(sys.argv)}")
        sys.exit(1)

    filename = str(sys.argv[1])

    files = []

    # If File
    if os.path.isfile(filename):
        if not os.path.splitext(filename)[1] == ".vm":
            print(f"Wrong File extenstion, please use .vm")
            sys.exit(1)
        files.append(filename)
        return files

    # If Folder
    if os.path.isdir(filename):
        for root, subdirList, fileList in os.walk(filename):
            for file in fileList:
                if os.path.splitext(file)[1] == ".vm":
                    files.append(os.path.join(root, file))
        return files

    # Not File or Folder
    print(Fore.RED + "ERROR: No File or Directory provided")
    sys.exit(1)


def BootstrapCode():
    return ["//Bootstrap"]


if __name__ == "__main__":
    main()

# %%
