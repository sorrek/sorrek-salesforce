from collections import OrderedDict
import copy
from datetime import datetime
import json
import math
import numpy as np
import os
import pandas as pd



def list_sfdc_objects(sf):
    objects = []
    query = "SELECT QualifiedApiName FROM EntityDefinition WHERE DurableId != null"
    r = sf.query_all(query)["records"]
    for result in r:
        objects.append(result["QualifiedApiName"])
    return objects


def list_sfdc_object_fields(sf, object):
    desc = getattr(sf, object).describe()
    fields = []
    for f in desc["fields"]:
        fields.append(f["name"])
    return fields


def list_object_dependencies(sf, object):
    desc = getattr(sf, object).describe()
    relationships = []
    for r in desc["childRelationships"]:
        if not r["deprecatedAndHidden"]:
            relationships.append({r["childSObject"] : r["field"]})
    return relationships


def get_object_data(sf, object, batch_size=10000):
    fields = list_sfdc_object_fields(object)
    base_query = f"SELECT {', '.join(fields)} FROM {object}"
    results = []
    last_id = ""
    while True:
        if last_id == "":
            r = sf.query_all(f"{base_query} ORDER BY Id LIMIT {batch_size}")["records"]
        else:
            r = sf.query_all(f"{base_query} WHERE Id > '{last_id}' ORDER BY Id LIMIT {batch_size}")["records"]
        for result in r:
            d = {}
            for field in fields:
                try:
                    d.update({field : result[field]})
                except:
                    continue
            results.append(copy.deepcopy(d))
        if len(r) != batch_size:
            break
        else:
            last_id = r[-1]["Id"]  
            continue
    df = pd.DataFrame(results)
    return df


def list_df_odict_columns(df):
    o_dict_cols = []
    for col in df.columns:
        if len(df[df[col].notna()]) == 0:
            continue
        else:
            v = df[df[col].notna()][col].iloc[0]
            if isinstance(v, OrderedDict):
                o_dict_cols.append(col)   
    return o_dict_cols


def df_odict_to_json(df):
    upload_df = df.copy()
    o_dict_cols = list_df_odict_columns(df)
    for col in o_dict_cols:
        upload_df[col] = upload_df[col].fillna(OrderedDict())
        upload_df[col] = upload_df[col].apply(lambda x: json.dumps(x))
    return upload_df


def update_object(sf, object, update_dicts, batch_size=1000):
    update_method = getattr(sf.bulk, object)
    chunks = math.ceil(len(update_dicts)/batch_size)
    results = []
    for i in range(0, chunks):
        chunk = update_dicts[i*batch_size:(i+1)*batch_size]
        result = update_method.update(chunk)
        results += result
    return results


def object_df_to_sql(df, sql_conn, schema, table_name):
    if not table_name[0].isalpha():
        table_name = f"o_{table_name}"
    upload_df = df_odict_to_json(df)
    upload_df.to_sql(table_name, sql_conn, schema=schema, if_exists="replace", index=False, chunksize=5000, method="multi")


def backup_salesforce(sf, sql_conn, schema, objects=[], batch_size=10000):
    if objects == []:
        objects = list_sfdc_objects(sf)
    print(f"Porting Data - {len(objects)} Objects to Back-up")
    sfdc_details = []
    i = 0
    for object in objects:
        i += 1
        print(f"Executing {object} ({i} of {len(objects)})")
        try:
            df = get_object_data(sf, object, batch_size=batch_size)
            object_df_to_sql(df, sql_conn, schema, object)
            print(f"\t{len(df)} records collected")
            sfdc_details.append({"object" : object, "record_count" : len(df), "status" : "success"})
        except:
            print(f"\t0 records collected")
            sfdc_details.append({"object" : object, "record_count" : 0, "status" : "failed"})
    print("Copying Back-up Details to Database")
    sfdc_details_df = pd.DataFrame(sfdc_details)
    print(f"Done ({len(sfdc_details_df[sfdc_details_df['status']=='failed'])} Failed)")
    return sfdc_details_df
