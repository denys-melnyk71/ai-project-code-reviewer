from pydantic import BaseModel, Field
from typing import List

class CodeIssue(BaseModel):
    category: str = Field(description="Категорія: 'PEP 8', 'Вразливість' або 'Рефакторинг'")
    line_number: str = Field(description="Номер рядка коду (або 'Всі', якщо стосується всього файлу)")
    description: str = Field(description="Опис проблеми українською мовою")
    suggestion: str = Field(description="Рекомендація щодо виправлення")

class ReviewResult(BaseModel):
    score: int = Field(description="Загальна оцінка коду від 1 до 10")
    summary: str = Field(description="Короткий загальний висновок від Senior Developer")
    issues: List[CodeIssue] = Field(description="Список знайдених проблем та зауважень")
    refactored_code: str = Field(description="Повний виправлений та оптимізований код")