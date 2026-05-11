<script lang="ts">
	import { resolve } from '$app/paths';
</script>

<svelte:head>
	<title>fplstat</title>
</svelte:head>

<section>
	<h1>fplstat</h1>
	<p>Self-service analytics for Fantasy Premier League players.</p>
	<ul>
		<li><a href={resolve('/fdr')}>FDR matrix</a> — fixture difficulty by team and gameweek</li>
	</ul>
</section>

<style>
	section {
		max-width: 720px;
		margin: 2rem auto;
		padding: 1rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
	}
</style>
