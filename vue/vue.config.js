const BundleTracker = require("webpack-bundle-tracker");

const pages = {
	chart: {
		entry: "./src/pages/chart/main.js",
	},
	exam: {
		entry: "./src/pages/exam/main.js",
	},
	subject: {
		entry: "./src/pages/subject/main.js",
	},
};
module.exports = {
	pages: pages,
	publicPath:
		process.env.NODE_ENV === "production"
			? "/static/dist/"
			: "http://127.0.0.1:8080",
	outputDir: "../server/static/dist",

	chainWebpack: (config) => {
		config.devServer
			.public("http://127.0.0.1:8080")
			.hotOnly(true)
			.headers({ "Access-Control-Allow-Origin": "*" })
			.writeToDisk((filePath) => filePath.endsWith("index.html"));

		config
			.plugin("BundleTracker")
			.use(BundleTracker, [{ filename: "../vue/webpack-stats.json" }]);

		config.resolve.alias.set("__STATIC__", "static");
	},
};
