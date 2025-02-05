#!/usr/bin/env python3

import os
import sys
import json
import subprocess as sub


def upgrade():
    global packagelinks
    """
    Reads in the new package list from GitHub
    """

    package = "packagelist"
    try:
        packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())
    except FileNotFoundError:
        os.system(f"sudo mkdir {os.path.expanduser('~')}/espm")
        open(f"{os.path.expanduser('~')}/espm/installed.json", "w").write("{}")
        packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())

    try:  
            print(f"Downloading \033[1mPackage List\033[0m")
            os.chdir(f"{os.path.expanduser('~')}/espm/")
            os.system(f"sudo rm -rf {package}")
            os.system(f"sudo rm -rf ESPMPACKAGELIST")
            os.system(f"git clone https://github.com/Ferriit/ESPMPACKAGELIST.git")
            os.system(f"sudo mv ESPMPACKAGELIST {package}")
            os.chdir(f"{package}/")

            packagedata = json.loads(open(f"espmdata.json", "r").read())

            packagedata["path"] = f"{os.path.expanduser('~')}/espm/{package}"
            packages[package] = packagedata

            open(f"{os.path.expanduser('~')}/espm/installed.json", "w").write(json.dumps(packages, indent=1))

            print(f"\033[32;1mSuccess:\033[0m \033[1mESPM\033[0m was updated successfully")

    except KeyError:
        print(f"\033[31;1mError:\033[0m Package \033[1m{package}\033[22m not found")


def install(package, flag):
    global packagelinks
    """
    Installs a package
    """

    try:
        packagelinks = update()
    except FileNotFoundError:
        packagelinks = {"packagelist": ["https://github.com/Ferriit/ESPMPACKAGELIST.git", "ESPMPACKAGELIST"]}
        upgrade()
        packagelinks = update()

    try:
        packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())
    except FileNotFoundError:
        os.system(f"sudo mkdir {os.path.expanduser('~')}/espm")
        open(f"{os.path.expanduser('~')}/espm/installed.json", "w").write("{}")
        packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())

    if package not in packages or flag == "-skip":
        if flag != "-skip":
            choice = {"y": True, "n": False}[input(f"Are you sure you want to install \033[1m{package}\033[22m? (y/n) :  ")[0].lower()]
        else:
            choice = True
        try:
            if choice:
                
                print(f"Installing \033[1m{package}\033[0m")
                os.chdir(f"{os.path.expanduser('~')}/espm/")
                os.system(f"sudo rm -rf {package}")
                print("Removing old folders")
                os.system(f"sudo rm -rf {packagelinks[package][1]}")
                print(f"Cloning Git repository ({packagelinks[package][0]})")
                os.system(f"git clone {packagelinks[package][0]}")
                os.system(f"sudo mv {packagelinks[package][1]} {package}")
                os.chdir(f"{package}/")

                print("Reading Package Data")
                packagedata = json.loads(open(f"espmdata.json", "r").read())

                packagedata["path"] = f"{os.path.expanduser('~')}/espm/{package}"
                packages[package] = packagedata

                print("Saving Package Data")
                open(f"{os.path.expanduser('~')}/espm/installed.json", "w").write(json.dumps(packages, indent=1))
                
                for i in packagedata["languageinstallcommands"]:
                    os.system(i)

                print("\033[1;34mINFO\033[0m: Installing dependencies")
                for i in packagedata["dependencies"]:
                    print(f"\033[1;34mINFO\033[0m: Installing dependency {i}")
                    install(i, flag)


                if packagedata["compile"]:
                    print("Compiling... ", end="")
                    if flag == "spkg":
                        os.system(f"sudo spkg install {packagedata['compiler']}")
                    os.system(packagedata["compilecommand"])
                    print("Done")

                print("Executing custom commands")
                for i in packagedata["execute"]:
                    print(f"\033[3m{i}")
                    os.system(i)

                print(f"\033[32;1mSuccess:\033[0m Package \033[1m{package}\033[0m was installed successfully")

        except KeyError:
            print(f"\033[31;1mError:\033[0m Package \033[1m{package}\033[22m not found")

        except Exception as e:
            print(f"\033[31;1mError:\033[0m {e}")
    
    else:
        print(f"\033[33;1mWarning\033[0m: Package \033[1m{package}\033[0m is already installed")


def reinstall(package):
    global packagelinks
    print(f"\033[34;1mInfo\033[0m: Reinstalling {package}")
    print(f"\033[34;1mInfo\033[0m: Uninstalling {package}")
    uninstall(package, "skip")
    print(f"\033[34;1mInfo\033[0m: Installing {package}")
    install(package, "-skip")


def upgradepackages():
    global packagelinks
    packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())
    print("\033[34;1mInfo\033[0m: Updating Package List")
    upgrade()
    packagelinks = update()
    print("\033[34;1mInfo\033[0m: Updating packages")
    for i in list(packages.keys()):
        print(i)
        if i != "packagelist":
            reinstall(i)

    print("\033[34;1mInfo\033[0m: Finalizing upgrade")

    return packagelinks


def uninstall(package, flag):
    global packagelinks
    """
    Uninstalls a package
    """
    packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())
    if package in packages:
        if flag != "skip":
            choice = {"y": True, "n": False}[input(f"Are you sure you want to uninstall \033[1m{package}\033[22m? (y/n) :  ")[0].lower()]
        else:
            choice = True
        if choice:
            print(f"\033[34;1mInfo\033[0m: Uninstalling {package}")
            os.system(f"sudo rm -rf {os.path.expanduser('~')}/espm/{package}")

            del packages[package]

            print("Removing Package Data")
            open(f"{os.path.expanduser('~')}/espm/installed.json", "w").write(json.dumps(packages, indent=1))

            print(f"\033[32;1mSuccess:\033[0m Package \033[1m{package}\033[0m was uninstalled successfully")

    else:
        print(f"\033[31;1mError\033[0m: Package {package} is not installed")


def List(flags):
    global packagelinks
    """
    Lists all installed packages
    """
    try:
        packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())
    except FileNotFoundError:
        os.system(f"sudo mkdir {os.path.expanduser('~')}/espm")
        packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())

    if "-json" not in flags:
        LST = list(packages.keys())
        out = f"\033[34;1mInfo\033[0m: Found {len(LST)} packages\n"

        for package in packages:
            out += f"\033[1m{package}\033[22m: Version: {packages[package]['version']}, Developer: {packages[package]['developer']}, Language: {packages[package]['language']}, Path: {packages[package]['path']}\n"
        
        print(out + "\033[0m")
    
    else:
        print(json.dumps(packages, indent=1))


def show(showpackage: str):
    global packagelinks
    packages = json.loads(open(f"{os.path.expanduser('~')}/espm/installed.json", "r").read())
    package = packages[showpackage]

    print(f"\033[34;1m{showpackage[0].upper() + showpackage[1:]}:\033[39m\nVersion:\033[0m {package['version']}\n\033[1mDeveloper:\033[0m {package['developer']}\n\033[1mLanguage:\033[0m {package['language']}\n\033[1mPath:\033[0m {package['path']}\n\033[1mDescription:\033[0m {package['description']}")


def update():
    global packagelinks
    """
    Updates package list to the one most recently installed
    """
    packagelinks = json.loads(open(f"{os.path.expanduser('~')}/espm/packagelist/packagelist.json").read())
    try:
        temp = open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "r").read()
        custompackagelst = json.loads(temp)
    except FileNotFoundError:
        print("\033[32;1mWarning\033[0m: Failed reading custom Package List")
        os.system(f"sudo mkdir {os.path.expanduser('~')}/espm/custompackages")
        open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "w").write("{}")
        custompackagelst = {}

    except json.decoder.JSONDecodeError:
        print("\033[32;1mWarning\033[0m: Failed reading custom Package List")
        os.system(f"sudo mkdir {os.path.expanduser('~')}/espm/custompackages")
        open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "w").write("{}")
        temp = open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "r").read()
        custompackagelst = json.loads(temp)

    for package in custompackagelst:
        packagelinks[package] = custompackagelst[package]
    
    return packagelinks

# "calium": ["https://github.com/Ferriit/CaliumLang.git", "CaliumLang"],


def addrepo(packagename: str, repo: str):
    global packagelinks
    reversedrepo = repo[::-1]
    name = reversedrepo[reversedrepo.find("tig.") + 4:reversedrepo.find("/")][::-1]

    try:
        custompackagelst = json.loads(open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "r").read())
        custompackagelst[packagename] = [repo, name]
        open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "w").write(json.dumps(custompackagelst))
    except FileNotFoundError:
        os.system(f"sudo mkdir {os.path.expanduser('~')}/espm/custompackages")
        open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "w").write(json.dumps("{}"))


def removerepo(packagename: str):
    global packagelinks
    try:
        custompackagelst = json.loads(open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "r").read())
        del custompackagelst[packagename]
        open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "w").write(json.dumps(custompackagelst))
    except FileNotFoundError:
        os.system(f"sudo mkdir {os.path.expanduser('~')}/espm/custompackages")
        open(f"{os.path.expanduser('~')}/espm/custompackages/packagelist.json", "w").write(json.dumps("{}"))


def showpackagelist():
    global packagelinks
    out = "\033[94;1mESPM Package list:\033[0m\n"
    for i in packagelinks:
        out += f"\033[34m{i}\033[0m: {packagelinks[i][0]}\n"
    print(out[:-1])


def search(package, flag):
    global packagelinks
    try:
        packagelistLST = list(packagelinks.keys())
        package = packagelistLST[packagelistLST.index(args[1])]
        if flag != "-json":
            print(f"\033[32;1mSuccess\033[0m: Package {package} was found\n\n{package[0].upper() + package[1:]}\n\033[1mGit Repository\033[0m: {packagelinks[package][0]}")
        else:
            print(json.dumps({"package": package, "URL": packagelinks[package][0]}))
            
    except ValueError:
        print(f"\033[31;1mError\033[0m: Package {package} was not found")


if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        if args[0] == "help":
            print(              
"""
ESPM (EdgeSoft Package Manager) is a Package Manager built for EdgeSoft tools (Like Calium and SPKG)
                  
\033[1minstall\033[0m: Installs a package. Requires sudo privileges.
    > sudo espm install <package>

\033[1muninstall\033[0m: Uninstalls a package. Requires sudo privileges.
    > sudo espm uninstall <package>

\033[1mreinstall\033[0m: Uninstalls and reinstalls a package. Requires sudo privileges.
    > sudo espm reinstall <package>

\033[1mupgrade\033[0m: Downloads the latest Package List. Requires sudo privileges.
    > sudo espm upgrade

\033[1mupdate\033[0m: Updates the loaded Package List to the latest installed one. Requires sudo privileges.
    > sudo espm update

\033[1madd-repository\033[0m: Adds a custom repository. Requires sudo privileges.
    > sudo espm add-repository <package-name> <Git-link>

    The <package-name> is the name you want to use when installing the package.

\033[1mremove-repository\033[0m: Removes a customly added repository. Requires sudo privileges.
    > sudo espm remove-repository <package-name>

\033[1mshow-package-list\033[0m: Shows the package list of all available packages.
    > sudo espm show-package-list

\033[1mshow\033[0m: Shows the info for a package. The package has to be installed. Requires sudo privileges.
    > sudo espm show <package-name>

\033[1msearch\033[0m: Searches the package list for a package. Requires sudo privileges.
    > sudo espm search <package-name>

\033[1mhelp\033[0m: Shows this help message.

\033[1mversion\033[0m: Shows the version.
""")
            sys.exit()

        elif args[0] == "version":
            print("\033[1mESMP version \033[34m0.0.3\033[0m")
            sys.exit()

        global packagelinks
        packagelinks = update()

        if args[0] == "install":
            if len(args[1:]) > 1:
                install(args[2], args[1])
            else:
                install(args[1], "")

        elif args[0] == "uninstall":
            uninstall(args[1], "")

        elif args[0] == "reinstall":
            reinstall(args[1])
    
        elif args[0] == "list":
            List(args[1:])

        elif args[0] == "upgrade":
            packagelinks = upgradepackages()
    
        elif args[0] == "update":
            upgrade()
            packagelinks = update()
    
        elif args[0] == "add-repository":
            addrepo(args[1], args[2])

        elif args[0] == "remove-repository":
            removerepo(args[1])

        elif args[0] == "show-package-list":
            showpackagelist()
    
        elif args[0] == "show":
            show(args[1])

        elif args[0] == "search":
            if len(args[1:]) > 1:
                search(args[2], args[1])
            else:
                search(args[1], "")

    except KeyError:
        print("\033[31;1mError:\033[0m Invalid Arguments. The help command is \"espm help\"")
