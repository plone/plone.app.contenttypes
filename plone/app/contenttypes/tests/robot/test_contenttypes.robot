*** Settings ***

Variables  plone/app/testing/interfaces.py
Variables  plone/app/contenttypes/tests/robot/variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

Resource  plone/app/contenttypes/tests/robot/library-settings.txt
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Test Cases ***

Scenario: Test Folderlisting
    Given a Folder  Test-Folder
      And a File  Test-File
      And a Image  Test-Image
      And a Collection  Test-Collection
#      And a Event  Test-Event 
      And a Link  Test-Link 
      And a News Item  Test-News 
      And a Document  Test-Document
     When I Go to  ${TEST_FOLDER}/folder_contents
     Then Page Should Contain  Test-Folder
      And Page Should Contain  Test-File
      And Page Should Contain  Test-Image
      And Page Should Contain  Test-Collection 
#      And Page Should Contain  Test-Event 
      And Page Should Contain  Test-Link 
      And Page Should Contain  Test-News 
      And Page Should Contain  Test-Document 


*** Keywords ***

I go to
    [Arguments]  ${location}
    Go to  ${location}
