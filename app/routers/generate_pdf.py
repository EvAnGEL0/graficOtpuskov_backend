from fastapi import FastAPI, HTTPException, APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app import models
from sqlalchemy.orm import selectinload
from io import BytesIO
from docx import Document
from docx.shared import Inches
import asyncio

router = APIRouter(
    prefix="/generate_pdf",
    tags=["generate_pdf"]
)

@router.post("/generate-vacation-schedule-docx/")
async def generate_vacation_schedule_docx(department_id: int, year: int, db: AsyncSession = Depends(get_db)):
    try:
        # Получаем имя отдела
        dept_result = await db.execute(
            select(models.Department_s).where(models.Department_s.id == department_id)
        )
        department = dept_result.scalar_one_or_none()

        if not department:
            raise HTTPException(status_code=404, detail="Отдел не найден")

        # Выполняем запрос к базе
        result = await db.execute(
            select(models.VacationSchedule)
            .options(
                selectinload(models.VacationSchedule.staff)
                .selectinload(models.Staff.position)
            )
            .join(models.Staff)
            .where(
                models.Staff.department_id == department_id,
                models.VacationSchedule.start_date >= f"{year}-01-01",
                models.VacationSchedule.end_date <= f"{year}-12-31"
            )
        )
        vacations_db = result.scalars().all()

        if not vacations_db:
            raise HTTPException(status_code=404, detail="Нет данных об отпусках для выбранного отдела и года")

        # Создаём документ
        doc = Document()
        doc.add_heading(f'График отпусков за {year} год (отдел: {department.name})', 0)

        # Добавляем таблицу
        table = doc.add_table(rows=1, cols=6)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Должность'
        hdr_cells[1].text = 'Фамилия'
        hdr_cells[2].text = 'Имя'
        hdr_cells[3].text = 'Отчество'
        hdr_cells[4].text = 'Кол-во дней'
        hdr_cells[5].text = 'Период отпуска'

        for vac in vacations_db:
            row_cells = table.add_row().cells
            row_cells[0].text = vac.staff.position.name if vac.staff.position else "Не указана"
            row_cells[1].text = vac.staff.last_name
            row_cells[2].text = vac.staff.first_name
            row_cells[3].text = vac.staff.middle_name or ""
            row_cells[4].text = str(vac.main_vacation_days)
            row_cells[5].text = f"{vac.start_date.strftime('%d.%m.%Y')} - {vac.end_date.strftime('%d.%m.%Y')}"

        # Добавляем подпись внизу
        doc.add_paragraph()
        doc.add_paragraph(f'Начальник отдела: _____________________________')

        # Сохраняем в BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        # Возвращаем файл
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=grafik_otpuska_{year}_{department.name}.docx"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации DOCX: {str(e)}")