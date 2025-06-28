from app.crud.company_crud import set_liked_companies


def update_liked_status(company_names: list[str]) -> dict:
    return set_liked_companies(company_names)
