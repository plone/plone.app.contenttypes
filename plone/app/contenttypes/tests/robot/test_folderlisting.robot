*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/contenttypes/tests/robot/keywords.txt

Variables  plone/app/contenttypes/tests/robot/variables.py


Test Setup  Run Keywords  Setup Testcontent  Plone test setup
Test Teardown  Run keywords  Plone test teardown

*** Variables ***

*** Test cases ***

Scenario: Test folder listing view
    Given I am logged in as site owner
    I disable dropdown navigation

    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/listing_view
    Then Listing should list contained content

Scenario: Test folder summary view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/summary_view
    Then Listing should list contained content

Scenario: Test folder tabular view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/tabular_view
    Then Listing should list contained content

Scenario: Test folder full view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/full_view
    Then Listing should list contained content in detail

Scenario: Test folder album view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_album/album_view
    Then Album should list contained images and albums

Scenario: Test collection listing view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/listing_view
    Then Listing should list all content

Scenario: Test collection summary view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/summary_view
    Then Listing should list all content

Scenario: Test collection tabular view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/tabular_view
    Then Listing should list all content

Scenario: Test collection full view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/full_view
    Then Listing should list all content in detail

Scenario: Test collection album view
    Given I am logged in as site owner
    I disable dropdown navigation
    When I Go to  ${PLONE_URL}/${TEST_FOLDER_ID}/test_collection/album_view
    Then Album should list all images and albums


*** Keywords ***

Listing should list contained content
  the content area should contain  Test Document
  the content area should contain  Test News Item
  the content area should contain  Test Event
  the content area should contain  Test Collection
  the content area should contain  Test Link
  the content area should contain  Test File
  the content area should contain  Test Image
  the content area should contain  Test Album
  the content area should not contain  Test Album Image 1
  the content area should not contain  Test Album Image 2
  the content area should not contain  Test Album Image 3
  the content area should not contain  Test Sub Album
  the content area should not contain  Test Sub Album Image 1
  the content area should not contain  Test Sub Album Image 2
  the content area should not contain  Test Sub Album Image 3

Listing should list contained content in detail
  the content area should contain  Test Document
  the content area should contain  this is a test document
  the content area should contain  Test News Item
  the content area should contain  this is a test news item
  Page Should Contain Element  //img[@title="Test News Item"]  2
  the content area should contain  Test Event
  the content area should contain  this is a test event
  the content area should contain  Test Collection
  the content area should contain  this is a test collection
  the content area should contain  Test Link
  the content area should contain  http://plone.org
  the content area should contain  Test File
  the content area should contain  file.pdf
  the content area should contain  Test Image
  Page Should Contain Element  //img[@title="Test Image"]  3
  the content area should contain  Test Album
  the content area should contain  Test Album Image 1
  Page Should Contain Element  //img[@title="Test Album Image 1"]  2
  the content area should contain  Test Album Image 2
  Page Should Contain Element  //img[@title="Test Album Image 2"]  2
  the content area should contain  Test Album Image 3
  Page Should Contain Element  //img[@title="Test Album Image 3"]  2
  the content area should contain  Test Sub Album
  the content area should contain  Test Sub Album Image 1
  Page Should Contain Element  //img[@title="Test Sub Album Image 1"]  1
  the content area should contain  Test Sub Album Image 2
  Page Should Contain Element  //img[@title="Test Sub Album Image 2"]  1
  the content area should contain  Test Sub Album Image 3
  Page Should Contain Element  //img[@title="Test Sub Album Image 3"]  1

Album should list contained images and albums
  the content area should contain  Test Album Image 1
  Page Should Contain Element  //img[@title="Test Album Image 1"]  2
  the content area should contain  Test Album Image 2
  Page Should Contain Element  //img[@title="Test Album Image 2"]  2
  the content area should contain  Test Album Image 3
  Page Should Contain Element  //img[@title="Test Album Image 3"]  2
  the content area should contain  Test Sub Album


Listing should list all content
  the content area should contain  Test Document
  the content area should contain  Test News Item
  the content area should contain  Test Event
  the content area should contain  Test Collection
  the content area should contain  Test Link
  the content area should contain  Test File
  the content area should contain  Test Image
  the content area should contain  Test Album
  the content area should contain  Test Album Image 1
  the content area should contain  Test Album Image 2
  the content area should contain  Test Album Image 3
  the content area should contain  Test Sub Album
  the content area should contain  Test Sub Album Image 1
  the content area should contain  Test Sub Album Image 2
  the content area should contain  Test Sub Album Image 3

Listing should list all content in detail
  the content area should contain  Test Document
  the content area should contain  this is a test document
  the content area should contain  Test News Item
  the content area should contain  this is a test news item
  Page Should Contain Element  //img[@title="Test News Item"]  2
  the content area should contain  Test Event
  the content area should contain  this is a test event
  the content area should contain  Test Collection
  the content area should contain  this is a test collection
  the content area should contain  Test Link
  the content area should contain  http://plone.org
  the content area should contain  Test File
  the content area should contain  file.pdf
  the content area should contain  Test Image
  Page Should Contain Element  //img[@title="Test Image"]  3
  the content area should contain  Test Album
  the content area should contain  Test Album Image 1
  Page Should Contain Element  //img[@title="Test Album Image 1"]  2
  the content area should contain  Test Album Image 2
  Page Should Contain Element  //img[@title="Test Album Image 2"]  2
  the content area should contain  Test Album Image 3
  Page Should Contain Element  //img[@title="Test Album Image 3"]  2
  the content area should contain  Test Sub Album
  the content area should contain  Test Sub Album Image 1
  Page Should Contain Element  //img[@title="Test Sub Album Image 1"]  2
  the content area should contain  Test Sub Album Image 2
  Page Should Contain Element  //img[@title="Test Sub Album Image 2"]  2
  the content area should contain  Test Sub Album Image 3
  Page Should Contain Element  //img[@title="Test Sub Album Image 3"]  2

Album should list all images and albums
  the content area should contain  Test Image
  Page Should Contain Element  //div[contains(@class, "card-image")]//img[@title="Test Image"]  1
  the content area should contain  Test News Item
  Page Should Contain Element  //div[contains(@class, "card-image")]//img[@title="Test News Item"]  1
  the content area should contain  Test Album Image 1
  Page Should Contain Element  //div[contains(@class, "card-image")]//img[@title="Test Album Image 1"]  1
  the content area should contain  Test Album Image 2
  Page Should Contain Element  //div[contains(@class, "card-image")]//img[@title="Test Album Image 2"]  1
  the content area should contain  Test Album Image 3
  Page Should Contain Element  //div[contains(@class, "card-image")]//img[@title="Test Album Image 3"]  1
  the content area should contain  Test Sub Album Image 1
  Page Should Contain Element  //div[contains(@class, "card-image")]//img[@title="Test Sub Album Image 1"]  1
  the content area should contain  Test Sub Album Image 2
  Page Should Contain Element  //div[contains(@class, "card-image")]//img[@title="Test Sub Album Image 2"]  1
  the content area should contain  Test Sub Album Image 3
  Page Should Contain Element  //div[contains(@class, "card-image")]//img[@title="Test Sub Album Image 3"]  1
  the content area should contain  Test Album
  the content area should contain  Test Sub Album


Setup Testcontent
  Given I am logged in as site owner
  Create Content  type=Document  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_document  title=Test Document  text=this is a test document
  Create Content  type=News Item  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_news_item  title=Test News Item  text=this is a test news item
  Create Content  type=Event  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_event  title=Test Event  text=this is a test event
  Create Content  type=Collection  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_collection  title=Test Collection  query=${COLLECTION_TEST_QUERY}  text=this is a test collection
  Create Content  type=Link  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_link  title=Test Link  remoteUrl=http://plone.org
  Create Content  type=File  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_file  title=Test File
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_image  title=Test Image
  Create Content  type=Folder  container=${PLONE_PATH}/${TEST_FOLDER_ID}  id=test_album  title=Test Album
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album  id=album_image_1  title=Test Album Image 1
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album  id=album_image_2  title=Test Album Image 2
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album  id=album_image_3  title=Test Album Image 3
  Create Content  type=Folder  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album  id=test_subalbum  title=Test Sub Album
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album/test_subalbum  id=subalbum_image_1  title=Test Sub Album Image 1
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album/test_subalbum  id=subalbum_image_2  title=Test Sub Album Image 2
  Create Content  type=Image  container=${PLONE_PATH}/${TEST_FOLDER_ID}/test_album/test_subalbum  id=subalbum_image_3  title=Test Sub Album Image 3

I go to
    [Arguments]  ${location}
    Go to  ${location}

I disable dropdown navigation
  Go to  ${PLONE_URL}/@@navigation-controlpanel
  Input Text  name=form.widgets.navigation_depth  1
  Set Focus To Element  css=#form-buttons-save
  Wait Until Element Is Visible  css=#form-buttons-save
  Click Button  Save
  Wait until page contains  Changes saved
