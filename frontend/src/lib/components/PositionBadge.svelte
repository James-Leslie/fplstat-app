<script lang="ts">
	import type { Position } from '$lib/api/types';

	let { position }: { position: Position } = $props();

	const labels: Record<Position, string> = { 1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD' };
	const colours: Record<Position, string> = {
		1: 'var(--pos-gk)',
		2: 'var(--pos-def)',
		3: 'var(--pos-mid)',
		4: 'var(--pos-fwd)'
	};
</script>

<span class="badge" style="background:{colours[position]}">{labels[position]}</span>

<style>
	.badge {
		display: inline-block;
		padding: 0.1em 0.45em;
		border-radius: 4px;
		font-size: 0.65rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: rgba(0, 0, 0, 0.75);
		white-space: nowrap;
	}
</style>
