"""Cenários REA limitados para câmera, séries, idiomas e pacote portátil."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def action(identifier, kind, selector, **options):
    return {"step_id": identifier, "action": kind, "locator": {"kind": "css", "selector": selector}, "timeout_ms": 30000, **options}


def select(identifier, selector, value):
    return action(identifier, "select_option", selector, value={"source": "literal", "value": value})


def scenario(actions, width=1280, height=800, portable=False):
    return {"browser": {"mode": "launch", "executable_path": "C:/Program Files/Google/Chrome/Application/chrome.exe", "headless": True},
            "start_url": {"url": "http://127.0.0.1:8788/" + ("Saber_Brasil_Offline.html" if portable else "")},
            "environment": {"viewport": {"width": width, "height": height, "device_scale_factor": 1}, "locale": "pt-BR", "timezone": "America/Recife", "reduced_motion": "reduce"},
            "actions": actions,
            "capture": {"after_each_step": ["accessibility"] if portable else ["dom"], "at_end": ["url", "dom", "accessibility", "screenshot"], "events": ["page-errors", "console", "network", "downloads"]}}


def main():
    ready = action("ready", "wait_for", "#subjects button:first-child", state="visible")
    desktop = [ready,
        action("zoom_in", "click", "#zoom-in"), action("zoom_in_twice", "click", "#zoom-in"),
        action("zoom_out", "click", "#zoom-out"),
        action("rotate_up", "press", "#graph", key="ArrowUp"),
        action("roll", "press", "#graph", key="q"),
        action("pan", "press", "#graph", key="Shift+ArrowRight"),
        action("fit_keyboard", "press", "#graph", key="Home"),
        select("brazil", "#school-system", "BR"), select("brazil_grade", "#grade", "3"),
        action("none", "click", "#subjects-none"), action("all", "click", "#subjects-reset"),
        select("usa", "#school-system", "US"), select("usa_grade", "#grade", "3"),
        select("england", "#school-system", "GB-ENG"), select("england_year", "#grade", "3"),
        select("japan", "#school-system", "JP"), select("japan_grade", "#grade", "3"),
        select("china", "#school-system", "CN"), select("china_grade", "#grade", "9"),
        select("english", "#language", "en"), select("japanese", "#language", "ja"),
        select("traditional_chinese", "#language", "zh-Hant"), select("portuguese", "#language", "pt-BR"),
        action("clear", "click", "#clear-filters"),
        action("search", "fill", "#search", value={"source": "literal", "value": "EF03MA01"}),
        action("select_concept", "click", "#search-results button:first-child"),
        action("focus_concept", "click", "#focus-topic"),
        action("show_detail", "click", "#show-details"),
        action("detail_ready", "wait_for", "#detail", state="visible"),
        action("close_detail", "click", "#detail-close"),
        action("reset_filters", "click", "#clear-filters"),
        action("export_search", "fill", "#search", value={"source": "literal", "value": "EF01CI01"}),
        action("export_list", "click", "#list-view"),
        action("export_json", "click", "#export-json"), action("export_csv", "click", "#export-csv"),
        action("return_graph", "click", "#graph-view"), action("clear_export_search", "click", "#clear-filters"),
        action("final_fit", "click", "#fit-all")]
    mobile = [ready, select("china", "#school-system", "CN"), select("china_grade", "#grade", "9"),
        select("traditional_chinese", "#language", "zh-Hant"),
        action("list", "click", "#list-view"), action("list_ready", "wait_for", "#results button:first-child", state="visible"),
        action("graph", "click", "#graph-view"), select("portuguese", "#language", "pt-BR"),
        action("reset_filters", "click", "#clear-filters"), action("final_fit", "click", "#fit-all")]
    portable = [ready, select("japan", "#school-system", "JP"), select("japan_grade", "#grade", "3"),
        select("japanese", "#language", "ja"), action("zoom_in", "click", "#zoom-in"),
        select("portuguese", "#language", "pt-BR"), action("reset_filters", "click", "#clear-filters"),
        action("final_fit", "click", "#fit-all")]
    for name, value in {"desktop": scenario(desktop), "mobile": scenario(mobile, 390, 844), "portable": scenario(portable, portable=True)}.items():
        target = ROOT / "evidence" / ("scenario_v2_" + name + ".json")
        if target.exists():
            raise FileExistsError("Preserve a geração anterior do cenário antes de repetir.")
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Três cenários de navegador gravados.")


if __name__ == "__main__":
    main()
