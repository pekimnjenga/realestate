/**
 * Tailwind CSS configuration for production builds.
 * This file is used by the Tailwind CLI / PostCSS to purge unused styles.
 */
module.exports = {
	content: [
		'./app/templates/**/*.html',
		'./app/**/*.py',
		'./app/static/js/**/*.js'
	],
	theme: {
		extend: {},
	},
	plugins: [],
}