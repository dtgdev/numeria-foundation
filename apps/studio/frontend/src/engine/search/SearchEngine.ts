import { Numeria } from "../Numeria";

export interface SearchResult {
  id: string;
  type: string;
  title: string;
  description?: string;
}

export async function searchUniverse(
  query: string,
): Promise<SearchResult[]> {
  const q = query.trim().toLowerCase();

  if (!q) {
    return [];
  }

  const canon = await Numeria.canon.list();

  return canon
    .filter((item: any) =>
      JSON.stringify(item)
        .toLowerCase()
        .includes(q),
    )
    .map((item: any) => ({
      id: item.id ?? item.slug ?? crypto.randomUUID(),
      type: item.type ?? "Canon",
      title:
        item.name ??
        item.title ??
        "Untitled",
      description:
        item.description ??
        "",
    }));
}
