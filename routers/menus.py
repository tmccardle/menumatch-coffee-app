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


def current_version_for_menu(menu_id: str):
    result = (
        supabase.table("menu_versions")
        .select("*")
        .eq("menu_id", menu_id)
        .eq("is_current", True)
        .order("version_number", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]
    fallback = (
        supabase.table("menu_versions")
        .select("*")
        .eq("menu_id", menu_id)
        .order("version_number", desc=True)
        .limit(1)
        .execute()
    )
    return fallback.data[0] if fallback.data else None


@router.post("/restaurants")
def create_restaurant(payload: RestaurantIn):
    result = supabase.table("restaurants").insert(payload.dict()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Could not create restaurant")
    return result.data[0]


@router.get("/restaurants")
def list_restaurants():
    restaurants = supabase.table("restaurants").select("*").order("created_at", desc=True).execute()
    rows = restaurants.data or []
    enriched = []
    for shop in rows:
        menus = (
            supabase.table("menus")
            .select("*")
            .eq("restaurant_id", shop["id"])
            .execute()
        )
        menu_payload = []
        characterization = {}
        for menu in menus.data or []:
            version = current_version_for_menu(menu["id"])
            raw = (version or {}).get("raw_menu") or {}
            parsed = (version or {}).get("parsed_menu") or raw
            chars = (version or {}).get("characterization") or {}
            if chars and not characterization:
                characterization = chars
            items = []
            if isinstance(parsed, dict):
                items = parsed.get("items") or []
                chars = {**((parsed.get("characterization") or {})), **chars}
            elif isinstance(parsed, list):
                items = parsed
            if not items:
                continue
            menu_payload.append({
                "id": menu.get("id"),
                "name": menu.get("title") or "Menu",
                "items": items,
                "characterization": chars,
            })
        shop_out = dict(shop)
        shop_out["neighborhood"] = shop.get("area") or shop.get("city") or ""
        shop_out["url"] = shop.get("website") or ""
        shop_out["characterization"] = characterization
        shop_out["menus"] = menu_payload
        enriched.append(shop_out)
    return enriched


@router.get("/")
def list_menus(restaurant_id: Optional[str] = None):
    query = supabase.table("menus").select("*")
    if restaurant_id:
        query = query.eq("restaurant_id", restaurant_id)
    result = query.execute()
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
