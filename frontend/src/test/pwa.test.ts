import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

describe("PWA Configuration", () => {
  const publicDir = path.resolve(__dirname, "../../public")
  const rootDir = path.resolve(__dirname, "../..")

  describe("Web App Manifest", () => {
    it("manifest.webmanifest_exists_in_public_folder", () => {
      const manifestPath = path.join(publicDir, "manifest.webmanifest")
      expect(fs.existsSync(manifestPath)).toBe(true)
    })

    it("manifest_contains_required_pwa_fields", () => {
      const manifestPath = path.join(publicDir, "manifest.webmanifest")
      const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"))

      expect(manifest.name).toBe("AI Life Tracker")
      expect(manifest.short_name).toBe("Life Tracker")
      expect(manifest.start_url).toBe("/")
      expect(manifest.display).toBe("standalone")
      expect(manifest.theme_color).toBeDefined()
      expect(manifest.background_color).toBeDefined()
    })

    it("manifest_contains_icons_for_mobile_and_desktop", () => {
      const manifestPath = path.join(publicDir, "manifest.webmanifest")
      const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"))

      expect(manifest.icons).toBeDefined()
      expect(Array.isArray(manifest.icons)).toBe(true)

      const sizes = manifest.icons.map((icon: { sizes: string }) => icon.sizes)
      expect(sizes).toContain("192x192")
      expect(sizes).toContain("512x512")
    })
  })

  describe("PWA Icons", () => {
    it("pwa_icon_192x192_exists", () => {
      const iconPath = path.join(publicDir, "pwa-192x192.png")
      expect(fs.existsSync(iconPath)).toBe(true)
    })

    it("pwa_icon_512x512_exists", () => {
      const iconPath = path.join(publicDir, "pwa-512x512.png")
      expect(fs.existsSync(iconPath)).toBe(true)
    })
  })

  describe("index.html PWA Meta Tags", () => {
    it("index_html_contains_theme_color_meta_tag", () => {
      const indexPath = path.join(rootDir, "index.html")
      const html = fs.readFileSync(indexPath, "utf-8")

      expect(html).toContain('name="theme-color"')
    })

    it("index_html_contains_manifest_link", () => {
      const indexPath = path.join(rootDir, "index.html")
      const html = fs.readFileSync(indexPath, "utf-8")

      expect(html).toContain('rel="manifest"')
      expect(html).toContain("manifest.webmanifest")
    })

    it("index_html_contains_apple_touch_icon_link", () => {
      const indexPath = path.join(rootDir, "index.html")
      const html = fs.readFileSync(indexPath, "utf-8")

      expect(html).toContain('rel="apple-touch-icon"')
    })

    it("index_html_has_proper_app_title", () => {
      const indexPath = path.join(rootDir, "index.html")
      const html = fs.readFileSync(indexPath, "utf-8")

      expect(html).toContain("<title>AI Life Tracker</title>")
    })
  })

  describe("Vite PWA Plugin Configuration", () => {
    it("vite_config_imports_vitepwa", () => {
      const viteConfigPath = path.join(rootDir, "vite.config.ts")
      const config = fs.readFileSync(viteConfigPath, "utf-8")

      expect(config).toContain("VitePWA")
      expect(config).toContain("vite-plugin-pwa")
    })
  })
})
