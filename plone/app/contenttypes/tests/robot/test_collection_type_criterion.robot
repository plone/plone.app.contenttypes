*** Settings ***

Library  Selenium2Library  timeout=2  implicit_wait=0.1

Resource  plone/app/contenttypes/tests/robot/keywords.txt
Variables  plone/app/testing/interfaces.py
Variables  plone/app/contenttypes/tests/robot/variables.py

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Test Cases ***

Test Short name (id) Criterion
    Given a document  Test Document
      And a news_item  Test News Item
      And a collection  My Collection
     When I set the collection's type criterion to  News Item
     Then the collection should contain  Test News Item
      And the collection should not contain  Test Document


*** Keywords ***

I set the collection's type criterion to
    [Arguments]  ${criterion}
    Click Link  Edit
    Wait Until Page Contains Element  xpath=//select[@name="addindex"]
    Select From List  xpath=//select[@name="addindex"]  Type

    Click Element  xpath=//span[@class='arrowDownAlternative']
    Select Checkbox  ${criterion}
    Click Button  Save
