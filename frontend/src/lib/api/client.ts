import { PUBLIC_API_BASE } from '$env/static/public';

export async function apiFetch<T>(
	path: string,
	params?: Record<string, string | number | undefined>
): Promise<T> {
	const url = new URL(PUBLIC_API_BASE + path);
	if (params) {
		for (const [key, value] of Object.entries(params)) {
			if (value !== undefined && value !== null) {
				url.searchParams.set(key, String(value));
			}
		}
	}
	const res = await fetch(url.toString());
	if (!res.ok) {
		throw new Error(`API error ${res.status} on ${path}`);
	}
	return res.json() as Promise<T>;
}
