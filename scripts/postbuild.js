const fs = require('fs');
const path = require('path');

// Post-build script for S3 deployment
// This script ensures proper handling of client-side routing

console.log('🔧 Running post-build configuration for S3 deployment...');

const buildPath = path.join(__dirname, '..', 'build');

// Create a custom 404.html file that redirects to index.html for client-side routing
const custom404 = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Provider Utility</title>
    <script>
        // Redirect to index.html for client-side routing
        window.location.replace('/index.html');
    </script>
</head>
<body>
    <p>Redirecting...</p>
</body>
</html>`;

try {
    // Write the custom 404.html file
    fs.writeFileSync(path.join(buildPath, '404.html'), custom404);
    console.log('✅ Created 404.html for client-side routing');

    // Create a robots.txt file to prevent indexing
    const robotsTxt = `User-agent: *
Disallow: /
`;

    fs.writeFileSync(path.join(buildPath, 'robots.txt'), robotsTxt);
    console.log('✅ Created robots.txt');

    // Create a sitemap.xml file
    const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://your-domain.com/</loc>
        <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>`;

    fs.writeFileSync(path.join(buildPath, 'sitemap.xml'), sitemapXml);
    console.log('✅ Created sitemap.xml');

    // Update index.html to include proper meta tags for S3 hosting
    const indexPath = path.join(buildPath, 'index.html');
    let indexContent = fs.readFileSync(indexPath, 'utf8');
    
    // Add meta robots noindex to prevent indexing and some additional meta tags
    const additionalMeta = `
    <meta name="robots" content="noindex, nofollow">
    <meta property="og:title" content="Provider Utility">
    <meta property="og:description" content="React frontend for AWS Lambda MariaDB integration">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://your-domain.com">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Provider Utility">
    <meta name="twitter:description" content="React frontend for AWS Lambda MariaDB integration">
    <link rel="canonical" href="https://your-domain.com">`;
    
    // Insert additional meta tags before closing head tag
    indexContent = indexContent.replace('</head>', `${additionalMeta}\n</head>`);
    
    fs.writeFileSync(indexPath, indexContent);
    console.log('✅ Updated index.html with SEO meta tags');

    console.log('🎉 Post-build configuration complete!');
    console.log('📦 Build is ready for S3 deployment');
    
} catch (error) {
    console.error('❌ Error during post-build:', error);
    process.exit(1);
}
