# import os
# import subprocess
# import sys
#
#
# "set VCTargetsPath=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Microsoft\VC\v160\"
# "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" ConsoleApplication3.sln
# "C:\Users\Eduard\source\repos\ConsoleApplication3\x64\Debug\ConsoleApplication3.exe"
#
#
# def start():
#     msbuild = os.getenv('MSBUILD_PATH', r"C:\Program Files (x86)\MSBuild\14.0\Bin\MSBuild.exe")
#     # project_output_dir = os.getenv('PROJECT_OUTPUT_DIR', r'.')
#
#     if not os.path.exists(msbuild):
#         raise Exception('not found msbuild')
#
#     projects = [
#         r"C:\Users\Eduard\source\repos\ConsoleApplication3\ConsoleApplication3.sln",
#         r"C:\Users\Eduard\source\repos\ConsoleApplication3\ConsoleApplication3\ConsoleApplication3.vcxproj"
#     ]
#     win32_targets = '/t:ProjectA:rebuild;ProjectB:rebuild;ProjectC:rebuild'
#     # x64_targets = '/t:ProjectA:rebuild;ProjectB:rebuild;ProjectC:rebuild'
#
#     # rebuild = '/t:Rebuild'
#     # debug = '/p:Configuration=Debug'
#     # release = '/p:Configuration=Release'
#     # x64 = '/p:Platform=x64'
#     win32 = '/p:Platform=Win32'
#     # xp_toolset = '/p:PlatformToolset=v110/v100/v90'
#
#     # msbuild %s.vcxproj /t:rebuild /p:configuration=VC90Release,platform=%s
#     # msbuild myproject.vcxproj /p:PlatformToolset=v90 /t:rebuild
#     # msbuild myproject.vcxproj /p:PlatformToolset=v110_xp /t:rebuild
#
#     # making command line to run
#     default = [msbuild]
#     default.append('/m:1')  # https://msdn.microsoft.com/en-us/library/ms164311.aspx
#
#     libs = default[:]
#     libs.append(projects[0])    # append a project/solution name to build command-line
#
#     # if build_arch_target == 'x86':
#     default.append(win32)
#     # win32 targets
#     default.append(win32_targets)
#
#     return default
#
#
# def build(lib_to_build):
#     # build_result = False
#
#     print('Build Start ************************')
#
#     process = subprocess.Popen(
#         args=lib_to_build, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
#     )
#
#     while True:
#         next_line = process.stdout.readline()
#         if next_line == b'' and process.poll() is not None:
#             break
#         sys.stdout.write(next_line.decode('cp1252'))a
#         sys.stdout.flush()
#
#     # output = process.communicate()[0]
#     exit_code = process.returncode
#
#     if exit_code == 0:
#         build_result = True
#         pass
#     else:
#         build_result = False
#
#     return build_result
#
#
# lib_to_build = start()
# print(build(lib_to_build))
