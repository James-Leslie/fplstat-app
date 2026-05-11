// Shared visual constants used across pages.

// FDR colour scheme: maps fixture difficulty rating (1-5) to (background, foreground).
export const FDR_COLOURS: Record<number, { bg: string; fg: string }> = {
	1: { bg: 'darkgreen', fg: 'white' },
	2: { bg: '#09fc7b', fg: 'black' },
	3: { bg: '#e7e7e8', fg: 'black' },
	4: { bg: '#ff1651', fg: 'white' },
	5: { bg: '#80072d', fg: 'white' }
};
