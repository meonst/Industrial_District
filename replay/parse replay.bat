@echo off
start cmd /k "python -m heroprotocol --details test.StormReplay > test\details.txt & python -m heroprotocol --gameevents test.StormReplay > test\gameevents.txt & python -m heroprotocol --messageevents test.StormReplay > test\messageevents.txt &  python -m heroprotocol --trackerevents test.StormReplay > test\trackerevents.txt & python -m heroprotocol --attributeevents test.StormReplay > test\attributeevents.txt & python -m heroprotocol --header test.StormReplay > test\header.txt & python -m heroprotocol --initdata test.StormReplay > test\initdata.txt & exit"

exit