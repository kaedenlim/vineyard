/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
      remotePatterns: [
        {
          protocol: 'https',
          hostname: 'img.lazcdn.com',
          port: '',
          pathname: '/**', // Allow any path on this hostname
        },
      ],
    },
  };
  
  export default nextConfig;
  