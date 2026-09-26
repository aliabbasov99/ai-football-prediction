/**
 * Ölkə → bayraq. Əvvəlcə lokal SVG (public/imgs/flags), yoxdursa emoji.
 * Emoji qurğu mövcud deyilsə də dəyişmir — sadəcə qısa bayraqlar göstərilir.
 */
const EMOJI: Record<string, string> = {
  England: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
  Spain: "🇪🇸",
  Germany: "🇩🇪",
  Italy: "🇮🇹",
  France: "🇫🇷",
  Netherlands: "🇳🇱",
  Portugal: "🇵🇹",
  Turkey: "🇹🇷",
  Brazil: "🇧🇷",
  Argentina: "🇦🇷",
  Belgium: "🇧🇪",
  "Saudi Arabia": "🇸🇦",
  USA: "🇺🇸",
  Greece: "🇬🇷",
  Czech: "🇨🇿",
  "Czech Republic": "🇨🇿",
  Ecuador: "🇪🇨",
  Denmark: "🇩🇰",
  Poland: "🇵🇱",
  Japan: "🇯🇵",
  Norway: "🇳🇴",
  China: "🇨🇳",
  Estonia: "🇪🇪",
  Belarus: "🇧🇾",
  Azerbaijan: "🇦🇿",
  Scotland: "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
  Wales: "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
  Ireland: "🇮🇪",
  Ukraine: "🇺🇦",
  Russia: "🇷🇺",
  Switzerland: "🇨🇭",
  Austria: "🇦🇹",
  Sweden: "🇸🇪",
};

export function countryFlag(country: string | null | undefined): string {
  if (!country) return "🏳️";
  return EMOJI[country] ?? "🏳️";
}
