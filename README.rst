Introduction
============

`Sorrek <http://www.sorrek.io>`__ is a data intelligence tool. This Python library provides several functions to read, update, and backup Salesforce. 

Installation
============

sorrek-salesforce releases are available as wheel packages for macOS, Windows and Linux on PyPi. Install it using ``pip``:

.. code-block:: bash

    python -m pip install -U pip
    python -m pip install -U sorrek-salesforce

Setup
=====

In order to use most of the methods included in this library, users will need to pass through a sf connection object using the `Simple Salesforce Python library <https://pypi.org/project/simple-salesforce/>`__. Please refer to their documentation on how to establish a Salesforce connection. 

Furthermore, some of the methods will require users to pass through a sql connection object using either a `SQLAlchemy <https://pypi.org/project/SQLAlchemy/>`__ or `psycopg2 <https://pypi.org/project/psycopg2/>`__ connector. 

Usage
=====

Listing all Salesforce objects
------------------------------
This lists all object API names from the ``EntityDefinition`` table. 
Use the ``list_sfdc_objects`` method:

.. code:: py

    from sorrek-salesforce import list_sfdc_objects

    objects = list_sfdc_objects(sf)

Listing all fields for a Salesforce object
------------------------------------------
This returns a list of all fields within the specified object.
Use the ``list_sfdc_object_fields`` method:

.. code:: py

    from sorrek-salesforce import list_sfdc_object_fields

    fields = list_sfdc_object_fields(sf, object)

Listing dependencies for a Salesforce object
--------------------------------------------
This lists all fields in an object and their respective lookup objects where that field is a lookup to another object. 
Use the ``list_object_dependencies`` method:

.. code:: py

    from sorrek-salesforce import list_object_dependencies

    fields = list_object_dependencies(sf, object)

Getting object data
-------------------
This returns a dataframe output of the full contents of a Salesforce object. The default ``batch_size`` is 10,000 records for each call.
Use the ``get_object_data`` method:

.. code:: py

    from sorrek-salesforce import get_object_data

    fields = get_object_data(sf, object, batch_size=10000)

**Note:** This method uses a single call to collect the fields for the object and additional call for every 10,000 records (using the default ``batch_size``). 

Working with Ordered Dictionary columns in a dataframe
------------------------------------------------------
Salesforce employs an Ordered Dictionary data type which is not compatible with some SQL databases and can be difficult to use. These methods help identify Ordered Dictionaries and convert them to JSONs. 
Use the ``list_df_odict_columns`` method to list dataframe columns that are Ordered Dictionaries:

.. code:: py

    from sorrek-salesforce import list_df_odict_columns

    odict_fields = list_df_odict_columns(df)

Use the ``df_odict_to_json`` method to convert dataframe columns that are Ordered Dictionaries into JSONs:

.. code:: py

    from sorrek-salesforce import df_odict_to_json

    df2 = df_odict_to_json(df)

Updating Salesforce records
---------------------------
This can be used to bulk update Salesforce objects with a variable object name. The update_dicts argument is a list of dictionaries with the ``Id`` value for the record and all other field and new value pairs. The default batch size is 1,000 records for each call.
Use the ``update_object`` method:

.. code:: py

    from sorrek-salesforce import update_object

    r = update_object(sf, object, update_dicts, batch_size=1000)

Porting Salesforce data to a SQL database
-----------------------------------------
Backing up Salesforce data in a SQL database is an effective and cost-efficient solution. These methods help to simplify the process of porting Salesforce data into a SQL database. 
Use the ``object_df_to_sql`` method to port a dataframe output from the ``get_object_data`` to a new SQL table:

.. code:: py

    from sorrek-salesforce import object_df_to_sql

    object_df_to_sql(df, sql_conn, schema, table_name)

Use the ``backup_salesforce`` method to automatically port all objects, or a pre-defined list of objects, from Salesforce to your SQL database:

.. code:: py

    from sorrek-salesforce import backup_salesforce

    sfdc_details_df = backup_salesforce(sf, sql_conn, schema, objects=[], batch_size=10000)

**Notes:**
    -   A ``sql_conn`` needs to be established using SQLAlchemy or psycopg2. Please refer to their documentation, linked above, for instructions on how to create this object. 
    -   By default, this method will backup all Salesforce objects. To select a subset of objects, use the objects argument. 
    -   The default batch size is 10,000 records for each call on each object. Please refer to the details in the section describing the ``get_object_data`` method for more details. 
    -   These methods will automatically convert any Ordered Dictionary data types into JSONs using the ``df_odict_to_json`` method.
    -   The ``backup_salesforce`` method will return a dataframe with details on how many records were collected from each object and which objects failed. In some cases, an object is shown in the ``EntityDefinition`` table but isn't actually queryable. 
