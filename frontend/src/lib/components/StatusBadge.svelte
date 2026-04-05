<script lang="ts">
	import type { PlayerStatus } from '$lib/api/types';

	let { status, news }: { status: PlayerStatus; news: string | null } = $props();

	const config: Record<PlayerStatus, { label: string; color: string }> = {
		a: { label: 'Avail', color: '#3ec984' },
		d: { label: 'Doubt', color: '#ff8f00' },
		i: { label: 'Inj', color: '#e84a4a' },
		s: { label: 'Susp', color: '#9c27b0' },
		u: { label: 'N/A', color: '#888' }
	};
</script>

{#if status !== 'a'}
	<span
		class="badge"
		style="background:{config[status].color}"
		title={news ?? config[status].label}
	>
		{config[status].label}
	</span>
{/if}

<style>
	.badge {
		display: inline-block;
		padding: 0.1em 0.45em;
		border-radius: 4px;
		font-size: 0.6rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #fff;
		white-space: nowrap;
		cursor: help;
	}
</style>
