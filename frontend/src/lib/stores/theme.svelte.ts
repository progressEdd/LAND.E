class ThemeState {
	mode = $state<'dark' | 'light'>('dark');

	get isDark() {
		return this.mode === 'dark';
	}

	toggle() {
		this.mode = this.mode === 'dark' ? 'light' : 'dark';
		if (typeof document !== 'undefined') {
			document.documentElement.classList.toggle('dark', this.isDark);
		}
	}
}

export const themeState = new ThemeState();
