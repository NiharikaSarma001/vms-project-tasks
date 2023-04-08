from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile, Query
from enum import Enum
from typing import Union, Optional
from fastapi.responses import FileResponse
from ..visitor.api import get_all_vendors, get_all_elt_visitors
import pathlib
import csv
import pandas as pd
import json
import xlsxwriter
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
        df.to_csv(file_name)
    elif file_format == FileFormat.xlsx:
        # Create Excel file
        #file_path = pathlib.Path(file_path) / f"{file_name}.xlsx"
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()
        for row_num, row_data in enumerate(data):
            for col_num, col_value in enumerate(row_data):
                worksheet.write(row_num, col_num, col_value)
        workbook.close()
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
    visitor_type: Optional[str] = Query(None, max_length=50),
) -> FileResponse:
    """export visitor report"""
    # if file_format not in ALLOWED_FORMATS:
    #     raise HTTPException(
    #         status_code=422, detail="Invalid file format. Allowed formats are CSV, XLSX, and JSON."
    #     )
    file_name = f"report.{file_format}"
    
    file_path = "C:\\Users\\Admin\\Downloads" # modify this to the desired directory path
    if visitor_type == "vendor":
        data = get_all_vendors({})
    elif visitor_type == "elt":
        data = get_all_elt_visitors()
    else:
        data = get_all_visitors()
    
    if create_file(data, file_format=file_format, file_name=file_name, file_path=file_path):
        media_type = MediaType.get_media_type(file_format)
        return FileResponse(file_name, media_type=media_type)

    else:
        raise HTTPException(
            status_code=500, detail="Failed to create report."
        )



# async def export_report(
#     file_format: FileFormat,
#     visitor_type: Optional[str] = Query(None, max_length=50),
# ) -> FileResponse:
#     """export visitor report"""
#     if file_format not in ALLOWED_FORMATS:
#         raise HTTPException(
#             status_code=422, detail="Invalid file format. Allowed formats are CSV, XLSX, and JSON."
#         )
#     file_name = f"report.{file_format}"
#     if visitor_type == "vendor":
#         data = get_all_vendors()
#     elif visitor_type == "elt":
#         data = get_all_elt_visitors()
#     else:
#         data = get_all_visitors()
#     if create_file(data, file_format=file_format, file_name=file_name):
#         return FileResponse(file_name, media_type=f"application/{file_format}")
#     else:
#         raise HTTPException(
#             status_code=500, detail="Failed to create report."
#         )


# @app.post("/reports/")
# async def create_report(report_file: UploadFile = File(...)):
#     allowed_formats = [ReportFormats.csv.value, ReportFormats.xlsx.value, ReportFormats.json.value]
#     file_format = report_file.filename.split(".")[-1]
#     if file_format not in allowed_formats:
#         raise HTTPException(status_code=422, detail="Invalid file format. Allowed formats are CSV, XLSX, and JSON.")
#     # Do something with the file here
#     return {"filename": report_file.filename, "format": file_format}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app", port=8000, reload=True)