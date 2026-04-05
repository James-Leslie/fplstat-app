<script lang="ts">
	let { fdr }: { fdr: number | null } = $props();

	const colours: Record<number, string> = {
		1: 'var(--fdr-1)',
		2: 'var(--fdr-2)',
		3: 'var(--fdr-3)',
		4: 'var(--fdr-4)',
		5: 'var(--fdr-5)'
	};
	const textColours: Record<number, string> = {
		1: '#fff',
		2: 'rgba(0,0,0,0.7)',
		3: 'rgba(0,0,0,0.5)',
		4: '#fff',
		5: '#fff'
	};
</script>

{#if fdr !== null && fdr !== undefined}
	<span
		class="badge"
		style="background:{colours[fdr] ?? '#ccc'}; color:{textColours[fdr] ?? '#000'}"
	>
		{fdr}
	</span>
{:else}
	<span class="none">—</span>
{/if}

<style>
	.badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 1.6em;
		height: 1.6em;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 700;
	}

	.none {
		color: rgba(0, 0, 0, 0.3);
	}
</style>
