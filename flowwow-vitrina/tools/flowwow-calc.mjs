#!/usr/bin/env node
// Калькулятор выплаты Flowwow по официальным ставкам из calculator.flowwow.info.
// Ставки проверены 09.11.2026 (списаны из бандла калькулятора).
// Использование:
//   node flowwow-calc.mjs 3000            — цена товара, СПб, цветы, доставка «Полный»
//   node flowwow-calc.mjs 3000 --half     — доставка «Половинка»
//   node flowwow-calc.mjs 3000 --none     — без пакета доставки
//   node flowwow-calc.mjs 3000 --self     — своя доставка (без удержания пакета)
//   node flowwow-calc.mjs 3000 --wowpass  — с WowPass (20% вместо 16%)
//   node flowwow-calc.mjs 3000 --cost=1800 — добавить себестоимость и маржу

const args = process.argv.slice(2);
const price = Number(args[0]);
if (!price || price <= 0) {
  console.error("Укажите цену товара: node flowwow-calc.mjs 3000 [--half|--none|--self|--wowpass|--cost=1800]");
  process.exit(2);
}

const VAT = 0.22; // НДС на комиссию и бонусы
const ACQUIRING = 0.025; // переменная комиссия от суммы товара (+доставки продавца)
const BONUS_MIN = 0.03; // минимальные бонусы клиенту, цветы
const FIXED = args.includes("--wowpass") ? 0.2 : 0.16; // Санкт-Петербург, цветы
const DELIVERY = args.includes("--self")
  ? 0
  : args.includes("--half")
    ? 153
    : args.includes("--none")
      ? 0
      : 336;
const cost = Number((args.find((a) => a.startsWith("--cost=")) || "").split("=")[1] || 0);

const fixed = price * FIXED;
const vatFixed = fixed * VAT;
const acquiring = price * ACQUIRING;
const bonus = price * BONUS_MIN;
const vatBonus = bonus * VAT;
const total = fixed + vatFixed + acquiring + bonus + vatBonus + DELIVERY;
const payout = price - total;
const pct = (total / price) * 100;

const rub = (n) => n.toLocaleString("ru-RU", { maximumFractionDigits: 0 }) + " ₽";

console.log(`Цена товара: ${rub(price)}`);
console.log(`Комиссия ${FIXED * 100}%: ${rub(fixed)}`);
console.log(`НДС на комиссию 22%: ${rub(vatFixed)}`);
console.log(`Эквайринг 2,5%: ${rub(acquiring)}`);
console.log(`Бонусы клиенту 3%: ${rub(bonus)} (+ НДС ${rub(vatBonus)})`);
console.log(`Пакет доставки: ${rub(DELIVERY)}`);
console.log(`Итого удержаний: ${rub(total)} (${pct.toFixed(1)}%)`);
console.log(`Выплата продавцу: ${rub(payout)}`);
if (cost > 0) {
  const margin = payout - cost;
  console.log(`Себестоимость: ${rub(cost)}`);
  console.log(`Маржа: ${rub(margin)} (${((margin / price) * 100).toFixed(1)}% от цены)`);
}
