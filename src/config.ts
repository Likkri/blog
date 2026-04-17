import type {
        ExpressiveCodeConfig,
        LicenseConfig,
        NavBarConfig,
        ProfileConfig,
        SiteConfig,
} from "./types/config";
import { LinkPreset } from "./types/config";

export const siteConfig: SiteConfig = {
        title: "覃科宁的博客",
        subtitle: "同济大学 · 材料科学与工程 · AI探索者",
        lang: "zh_CN",
        themeColor: {
                hue: 200,
                fixed: false,
        },
        banner: {
                enable: false,
                src: "assets/images/demo-banner.png", // Relative to the /src directory. Relative to the /public directory if it starts with '/'
                position: "center", // Equivalent to object-position, only supports 'top', 'center', 'bottom'. 'center' by default
                credit: {
                        enable: false, // Display the credit text of the banner image
                        text: "", // Credit text to be displayed
                        url: "", // (Optional) URL link to the original artwork or artist's page
                },
        },
        toc: {
                enable: true, // Display the table of contents on the right side of the post
                depth: 2, // Maximum heading depth to show in the table, from 1 to 3
        },
        favicon: [
                // Leave this array empty to use the default favicon
                // {
                //   src: '/favicon/icon.png',    // Path of the favicon, relative to the /public directory
                //   theme: 'light',              // (Optional) Either 'light' or 'dark', set only if you have different favicons for light and dark mode
                //   sizes: '32x32',              // (Optional) Size of the favicon, set only if you have favicons of different sizes
                // }
        ],
};

export const navBarConfig: NavBarConfig = {
        links: [
                LinkPreset.Home,
                LinkPreset.Archive,
                LinkPreset.About,
                {
                        name: "GitHub",
                        url: "https://github.com/Likkri",
                        external: true,
                },
        ],
};

export const profileConfig: ProfileConfig = {
        avatar: "assets/images/demo-avatar.png",
        name: "覃科宁",
        bio: "同济大学材料科学与工程学士 | AI创业探索者 | 全栈开发者",
        links: [
                {
                        name: "GitHub",
                        icon: "fa6-brands:github",
                        url: "https://github.com/Likkri",
                },
        ],
};

export const licenseConfig: LicenseConfig = {
        enable: true,
        name: "CC BY-NC-SA 4.0",
        url: "https://creativecommons.org/licenses/by-nc-sa/4.0/",
};

export const expressiveCodeConfig: ExpressiveCodeConfig = {
        // Note: Some styles (such as background color) are being overridden, see the astro.config.mjs file.
        // Please select a dark theme, as this blog theme currently only supports dark background color
        theme: "github-dark",
};
