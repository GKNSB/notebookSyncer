#!/usr/bin/env python3

import json
from glob import glob
from argparse import ArgumentParser

parser = ArgumentParser(prog="notebookSyncer.py", description="Sync code and markdown blocks in jupyter notebooks")
parser.add_argument("-s", "--source", action="store", dest="mySource", help="source ipynb file", type=str, default=None)
parser.add_argument("-t", "--target", action="store", dest="myTarget", help="target ipynb file or directory", type=str, default=None)
parser.add_argument("-d", "--directory", action="store_true", dest="isDirectory", help="if target is a directory", default=False)
args = parser.parse_args()

if not args.mySource or not args.myTarget:
    parser.print_usage()

targetFiles = []
if args.isDirectory:
    targetFiles = glob(f"{args.myTarget}/*.ipynb")
else:
    targetFiles = [args.myTarget]

for afile in targetFiles:
    if afile.endswith(args.mySource):
        targetFiles.remove(afile)

with open(args.mySource) as infile:
    dataSource = json.load(infile)

for aTarget in targetFiles:
    print(f"- Syncing {args.mySource} with {aTarget}")

    with open(aTarget) as infile2:
        dataTarget = json.load(infile2)

    with open(aTarget, "w") as outfile:

        for i in range(0,len(dataSource["cells"])):
            sourceCell = dataSource["cells"][i]

            try:
                targetCell = dataTarget["cells"][i]

                if sourceCell["cell_type"] == "markdown" and targetCell["cell_type"] == "markdown":
                    if sourceCell["source"] == targetCell["source"]:
                        #print("Matching markdown cell:", sourceCell["source"])
                        pass

                    else:
                        #print("Diff:", sourceCell["source"])
                        targetCell["source"] = sourceCell["source"]
                        dataTarget["cells"][i] = targetCell

                elif sourceCell["cell_type"] == "code" and targetCell["cell_type"] == "code":
                    if sourceCell["source"] == targetCell["source"]:
                        #print("Matching code cell:", sourceCell["id"])
                        pass

                    else:
                        #print("Diff:", sourceCell["id"])

                        for line in targetCell["source"]:
                            if line.startswith("bountyName"):
                                bountyNameLine = line
                            if line.startswith("domains"):
                                domainsLine = line

                        targetCell["source"] = sourceCell["source"]

                        for j in range(0,len(targetCell["source"])):
                            if targetCell["source"][j].startswith("bountyName"):
                                targetCell["source"][j] = bountyNameLine
                            if targetCell["source"][j].startswith("domains"):
                                targetCell["source"][j] = domainsLine

                        dataTarget["cells"][i] = targetCell

                else:
                    targetCell = sourceCell

                    if targetCell["cell_type"] == "code":
                        targetCell["outputs"] = []
                        targetCell["execution_count"] = None

                    dataTarget["cells"][i] = targetCell

            except IndexError:
                #print("New:", sourceCell["id"])
                tmpCell = sourceCell

                if tmpCell["cell_type"] == "code":
                    tmpCell["outputs"] = []
                    tmpCell["execution_count"] = None

                dataTarget["cells"].append(tmpCell)

        json.dump(dataTarget, outfile, indent=1)
