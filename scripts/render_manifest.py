"""이미지 이름을 단일 원본 K8s 매니페스트에 치환하여 rendered.yaml 생성."""
import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--image", required=True, help="예: myid/chatops-csms-lab:v1")
p.add_argument("--output", default="k8s/rendered.yaml")
a = p.parse_args()
if ":" not in a.image or "REPLACE" in a.image:
    p.error("태그가 포함된 실제 Docker Hub 이미지 이름을 사용하세요.")
source = Path("k8s/02-apps.yaml").read_text(encoding="utf-8")
target = Path(a.output)
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(source.replace("__IMAGE__", a.image), encoding="utf-8")
print("Rendered:", target, "Image:", a.image)
