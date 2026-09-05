from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from database import supabase

router = APIRouter(prefix="/menus", tags=["menus"])


class RestaurantIn(BaseModel):
    name: str
    city: Optional[str] = None
    area: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None


class MenuIn(BaseModel):
    restaurant_id: str
    title: Optional[str] = "Main menu"


class VersionIn(BaseModel):
    menu_id: str
    raw_menu: Any
    parsed_menu: Optional[Any] = None
    characterization: Optional[Any] = None
    notes: Optional[str] = None


@router.post("/restaurants")
def create_restaurant(payload: RestaurantIn):
    result = supabase.table("restaurants").insert(payload.dict()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Could not create restaurant")
    return result.data[0]


@router.get("/restaurants")
def list_restaurants():
    result = supabase.table("restaurants").select("*").order("created_at", desc=True).execute()
    return result.data


@router.post("/")
def create_menu(payload: MenuIn):
    result = supabase.table("menus").insert(payload.dict()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Could not create menu")
    return result.data[0]


@router.post("/versions")
def create_version(payload: VersionIn):
    existing = (
        supabase.table("menu_versions")
        .select("version_number")
        .eq("menu_id", payload.menu_id)
        .order("version_number", desc=True)
        .limit(1)
        .execute()
    )
    next_version = 1
    if existing.data:
        next_version = existing.data[0]["version_number"] + 1

    row = {
        "menu_id": payload.menu_id,
        "version_number": next_version,
        "raw_menu": payload.raw_menu,
        "parsed_menu": payload.parsed_menu or payload.raw_menu,
        "characterization": payload.characterization or {},
        "notes": payload.notes,
        "is_current": True,
    }
    result = supabase.table("menu_versions").insert(row).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Could not create menu version")
    return result.data[0]


@router.get("/{menu_id}/versions")
def list_versions(menu_id: str):
    result = (
        supabase.table("menu_versions")
        .select("*")
        .eq("menu_id", menu_id)
        .order("version_number", desc=True)
        .execute()
    )
    return result.data
