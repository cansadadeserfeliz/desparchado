const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
console.log(path.resolve(__dirname, '../desparchado/static/dist'));

module.exports = {
    entry: {
        main: './desparchado/static/src/js/main',
        dashboard: './desparchado/static/src/js/dashboard'
    },
    output: {
        filename: 'js/[name].[fullhash].js',
        path: path.resolve(__dirname, '../desparchado/static/dist'),
        clean: true,
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                exclude: /node_modules/,
                use: 'ts-loader'
            },
            {
                test: /\.s[ac]ss$/i,
                exclude: /node_modules/,
                use: [
                    // Creates `style` nodes from JS strings
                    MiniCssExtractPlugin.loader,  // replaces 'style-loader'
                    // Translates CSS into CommonJS
                    'css-loader',
                    // PostCSS
                    {
                        loader:'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: [
                                    ['postcss-preset-env', {}]
                                ]
                            }
                        }
                    },
                    // Compiles Sass to CSS
                    'sass-loader',
                ]
            },
        ]
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js']
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new MiniCssExtractPlugin({
            filename: 'css/[name]-[hash].css',
            chunkFilename: '[id]-[hash].css'
        }),
    ],
}
