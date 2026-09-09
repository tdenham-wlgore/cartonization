from pathlib import Path

from openpyxl import Workbook

from cartonization.io import build_shipment_profiles, load_reference_mapping, read_xlsx_as_dicts


def _write_sample_workbook(path: Path) -> None:
    wb = Workbook()

    ws = wb.active
    ws.title = "history"
    ws.append(["FREQUENCY", "C1", "C2"])
    ws.append([2, 1, 0])
    ws.append([3, 1, 0])
    ws.append([1, 0, 2])

    ws_ref = wb.create_sheet("reference")
    ws_ref.append(["ID", "LENGTH", "WIDTH", "HEIGHT"])
    ws_ref.append(["C1", 1, 2, 3])
    ws_ref.append(["C2", 4, 5, 6])

    wb.save(path)


def test_read_xlsx_as_dicts(tmp_path: Path):
    xlsx = tmp_path / "sample.xlsx"
    _write_sample_workbook(xlsx)

    rows = read_xlsx_as_dicts(str(xlsx), sheet_name="reference", usecols=["ID", "LENGTH"])
    assert rows == [
        {"ID": "C1", "LENGTH": 1},
        {"ID": "C2", "LENGTH": 4},
    ]


def test_load_reference_mapping(tmp_path: Path):
    xlsx = tmp_path / "sample.xlsx"
    _write_sample_workbook(xlsx)

    mapping = load_reference_mapping(
        ref_file=str(xlsx),
        sheet_name="reference",
        usecols=["ID", "LENGTH", "WIDTH", "HEIGHT"],
        id_col="ID",
        allowed_ids=["C1"],
        build_value=lambda r: (float(r["LENGTH"]), float(r["WIDTH"]), float(r["HEIGHT"])),
    )

    assert mapping == {"C1": (1.0, 2.0, 3.0)}


def test_build_shipment_profiles(tmp_path: Path):
    xlsx = tmp_path / "sample.xlsx"
    _write_sample_workbook(xlsx)

    profiles = build_shipment_profiles(
        history_file=str(xlsx),
        sheet_name="history",
        carton_list=["C1", "C2"],
        frequency_col="FREQUENCY",
    )

    # Two rows share the same counts [1,0] so frequency should sum to 5
    assert {tuple(p["counts"].values()): p["frequency"] for p in profiles} == {
        (1, 0): 5,
        (0, 2): 1,
    }
