*** Settings ***

Library  Remote  ${PLONE_URL}/RobotRemote

Variables  variables.py

*** Keywords ***

I am logged in as site owner
  Enable autologin as  Site Administrator

Click Edit
  Click Link  xpath=//a[contains(., "Edit")]

# ----------------------------------------------------------------------------
# Content
# ----------------------------------------------------------------------------

a collection
  [Arguments]  ${title}
  [Return]  ${uid}
  ${uid} =  Create content  type=Collection  title=${title}

a document
  [Arguments]  ${title}
  [Return]  ${uid}
  ${uid} =  Create content  type=Document  title=${title}

a event
  [Arguments]  ${title}
  [Return]  ${uid}
  ${uid} =  Create content  type=Event  title=${title}

a file
  [Arguments]  ${title}
  Go to  ${PLONE_URL}/++add++File
  Fill text  name=form.widgets.title  ${title}
  Choose File  name=form.widgets.file  ${PATH_TO_TEST_FILES}/file.pdf
  Click  css=#form-buttons-save
  Get text  body  contains  Item created

a folder
  [Arguments]  ${title}
  [Return]  ${uid}
  ${uid} =  Create content  type=Folder  title=${title}

a image
  [Arguments]  ${title}
  Go to  ${PLONE_URL}/++add++Image
  Fill text  name=form.widgets.title  ${title}
  Choose File  name=form.widgets.image  ${PATH_TO_TEST_FILES}/image.png
  Click  css=#form-buttons-save
  Get text  body  contains  Item created

a link
  [Arguments]  ${title}
  [Return]  ${uid}
  ${uid} =  Create content  type=Link  title=${title}


a news item
  [Arguments]  ${title}
  Go to  ${PLONE_URL}/++add++News Item
  Fill text  css=[name="form.widgets.IDublinCore.title"]  ${title}
  Click  css=#form-buttons-save
  Get text  body  contains  Item created


# ----------------------------------------------------------------------------
# Collection
# ----------------------------------------------------------------------------

the content area should contain
  [Arguments]  ${text}
  Get text  id=content  contains  ${text}

the content area should not contain
  [Arguments]  ${text}
  Get Text  id=content  !=  ${text}

the collection should contain
  [Arguments]  ${title}
  Get Element  //*[@id='content-core']//article//a[contains(text(), '${title}')]

the collection should not contain
  [Arguments]  ${title}
  The content area should not contain  ${title}

fill date field
  [Arguments]  ${fieldid}  ${year}=2012  ${month}=January  ${day}=10
  [Documentation]  Fill in the specified date field (such as effective/expiration date in the "dates" metadata tab) with the specified date.
  ...  Month must be specified by name.
  Click Element  xpath=//div[@data-fieldname="${fieldid}"]//input[contains(@class,"pattern-pickadate-date")]
  Select from list  css=div[data-fieldname="${fieldid}"] .picker__select--month  ${month}
  Select from list  css=div[data-fieldname="${fieldid}"] select.picker__select--year  ${year}
  Click Element  xpath=//div[@data-fieldname="${fieldid}"]//div[contains(@class, 'picker__day')][contains(text(), "${day}")]

I set the criteria ${type} in row ${number} to the option '${label}'
  ${criteria_row} =  Convert to String  .querystring-criteria-wrapper:nth-child(${number})
  Click  css=${criteria_row} .querystring-criteria-${type} .select2-choice
  Fill Text  css=#select2-drop input  ${label}
  Click  xpath=//*[@id="select2-drop"]//*[@class="select2-match"]

I set the criteria ${type} in row ${number} to the options '${label}'
    ${criteria_row} =  Convert to String  .querystring-criteria-wrapper:nth-child(1)
    Click  css=${criteria_row} .querystring-criteria-value .select2-choices
    Fill text  css=.select2-input.select2-focused  ${label}\n
    Click  css=.select2-highlighted
    Get text  css=${criteria_row} .select2-search-choice  contains  ${label}
    [Documentation]  Chrome needs some more time
    Sleep  .1s

I set the criteria ${type} in row ${number} to the text '${label}'
  ${criteria_row} =  Convert to String  .querystring-criteria-wrapper:nth-child(${number})
  Fill text  css=${criteria_row} .querystring-criteria-value input  ${label}
  Click  css=.autotoc-level-1.active
  Sleep  1s