from material_processor import MaterialProcessor
from tutor import Tutor
from user_registry import UserRegistry


def bootstrap_user() -> str:
    registry = UserRegistry()
    existing = registry.list_users()
    if existing:
        print("Known users:", ", ".join(existing))

    user_id = input("Enter your user id: ").strip() or "default"
    registry.ensure_user(user_id)
    return user_id


def collect_material(processor: MaterialProcessor) -> dict:
    print("\nMaterial source options:")
    print("1. Paste raw text")
    print("2. Upload file path")
    print("3. Provide web link")

    choice = input("Choose source (1/2/3): ").strip()

    title = input("Optional title (press Enter to auto-title): ").strip() or None

    if choice == "1":
        payload = input("Paste material text: ").strip()
        return processor.process("raw_text", payload, title=title)

    if choice == "2":
        payload = input("Enter local file path: ").strip()
        return processor.process("file", payload, title=title)

    if choice == "3":
        payload = input("Enter web link: ").strip()
        return processor.process("web_link", payload, title=title)

    raise ValueError("Invalid source selection.")


def main():
    user_id = bootstrap_user()
    tutor = Tutor(user_id=user_id)
    processor = MaterialProcessor()

    material = collect_material(processor)
    tutor.resume_or_explain_section(material["title"], material["content"])

    print("\nProgress summary:", tutor.get_progress_summary())


if __name__ == "__main__":
    main()
