*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Variables  plone/app/contenttypes/tests/robot/variables.py

Test Setup  Run keywords  Open test browser
Test Teardown  Close all browsers

*** Variables ***

*** Test cases ***

Scenario: Test Folderlisting
    Given I am logged in as site owner
      And a Folder  Test-Folder
      And a File  Test-File
      And a Image  Test-Image
      And a Collection  Test-Collection
      And a Event  Test-Event
      And a Link  Test-Link
      And a News Item  Test-News
      And a Document  Test-Document
     When I Go to  ${PLONE_URL}/folder_contents
     Then Page Should Contain  Test-Folder
      And Page Should Contain  Test-File
      And Page Should Contain  Test-Image
      And Page Should Contain  Test-Collection
      And Page Should Contain  Test-Event
      And Page Should Contain  Test-Link
      And Page Should Contain  Test-News
      And Page Should Contain  Test-Document


*** Keywords ***

I go to
    [Arguments]  ${location}
    Go to  ${location}
