from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile, Query, BackgroundTasks, Security
from enum import Enum
from typing import Union, Optional, List
from fastapi.responses import FileResponse
from ..visitor.api import get_all_vendors, get_all_elt_visitors, get_all_visitors
from ..employee.api import get_all_employee_data
from ..scopes import scope_settings
from ..visit.api import view_visit_query_datewise
from authentication.api import get_current_user
import pathlib
import csv
import pandas as pd
import json
import xlsxwriter
from fastapi.encoders import jsonable_encoder

#from reports import router as reports_router


app = APIRouter()
#app.include_router(reports_router)

class FileFormat(str, Enum):
    csv = "csv"
    xlsx = "xlsx"
    json = "json"

ALLOWED_FORMATS = [FileFormat.csv, FileFormat.xlsx, FileFormat.json]

#@app.get("/reports/")

class MediaType(str, Enum):
    xlsx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    csv = "text/csv"
    json = "application/json"
    
    def get_media_type(self, file_format: FileFormat) -> str:
        if file_format == FileFormat.csv:
            return MediaType.csv
        elif file_format == FileFormat.xlsx:
            return MediaType.xlsx
        elif file_format == FileFormat.json:
            return MediaType.json
        else:
            return MediaType.csv  # default to CSV media type


def create_file(data, file_format, file_name, file_path):

    if file_format == FileFormat.csv:
        # Create CSV file
        #file_path = pathlib.Path(file_path) / f"{file_name}.csv"
        # with open(file_name, mode="w", newline="") as file:
        #     writer = csv.writer(file)
        #     writer.writerows(data)
        df=pd.DataFrame(data)
        df.to_csv(file_name, index=False)
        
    elif file_format == FileFormat.xlsx:
        # Create Excel file
        #file_path = pathlib.Path(file_path) / f"{file_name}.xlsx"
        df=pd.DataFrame(data)
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        # workbook = xlsxwriter.Workbook(file_name)
        # worksheet = workbook.add_worksheet()
        # for row_num, row_data in enumerate(data):
        #     for col_num, col_value in enumerate(row_data):
        #         worksheet.write(row_num, col_num, col_value)
        # workbook.close()
    elif file_format == FileFormat.json:
        # Create JSON file
        #file_path = pathlib.Path(file_path) / f"{file_name}.json"
        with open(file_name, mode="w") as file:
            json.dump(data, file)
    else:
        return False
    return True

@app.get("/reports/")
async def export_report(
    file_format: FileFormat,
    file_name: Optional[str] = None,
    background_tasks:BackgroundTasks,
    visitor_type: Optional[str] = Query(None, max_length=50),
    to_date: Optional[str] = Query(None, max_length=50),
    from_date:Optional[str] = Query(None, max_length=50)
)-> FileResponse:
    """export visitor report"""
    # if file_format not in ALLOWED_FORMATS:
    #     raise HTTPException(
    #         status_code=422, detail="Invalid file format. Allowed formats are CSV, XLSX, and JSON."
    #     )
    



    file_path = "C:\\Users\\Admin\\Downloads" 
    data=None
    if visitor_type == "vendor":
        data = await get_all_vendors({})
    elif visitor_type == "elt":
        data = await get_all_elt_visitors({})
    elif visitor_type == "employee":
        data = await get_all_employee_data({})
        data = jsonable_encoder(data)
    #data = list(data.values()
    
    elif visitor_type == "visit":
        data = await view_visit_query_datewise(
    from_date,
    to_date,
    user_data={},
    #visit_location=visit_location,
    background_tasks=background_tasks,
    alldata=True,
    
)      
        print(data)
    #     return await generate_report(
    # data=data,
    # from_date=from_date,
    # to_date=to_date,
    # #background_task=background_tasks,
    # file_format=file_format,
#)
    elif visitor_type is None:
        data = await get_all_visitors({})
    else:
        raise HTTPException(status_code=400, detail="Invalid visitor type")


    
    if create_file(data, file_format=file_format, file_name="reception.xlsx", file_path=file_path):
        media_type = MediaType[file_format]
        return FileResponse("reception.xlsx", media_type=media_type)

    else:
        raise HTTPException(
        status_code=500, detail="Failed to create report."
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app", port=8000, reload=True)
