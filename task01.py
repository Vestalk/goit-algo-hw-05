import timeit
from pathlib import Path

# ---------------------------- Боєр-Мур ----------------------------

def build_shift_table(pattern):
	"""Таблиця зсувів (евристика «поганого символу»)."""
	table = {}
	length = len(pattern)
	for index, char in enumerate(pattern[:-1]):
		table[char] = length - index - 1
	table.setdefault(pattern[-1], length)
	return table

def boyer_moore_search(text, pattern):
	shift_table = build_shift_table(pattern)
	i = 0
	while i <= len(text) - len(pattern):
		j = len(pattern) - 1
		while j >= 0 and text[i + j] == pattern[j]:
			j -= 1
		if j < 0:
			return i
		i += shift_table.get(text[i + len(pattern) - 1], len(pattern))
	return -1

# ---------------------- Кнут-Морріс-Пратт ----------------------

def compute_lps(pattern):
	"""Масив найдовших префіксів, що є суфіксами."""
	lps = [0] * len(pattern)
	length = 0
	i = 1
	while i < len(pattern):
		if pattern[i] == pattern[length]:
			length += 1
			lps[i] = length
			i += 1
		elif length != 0:
			length = lps[length - 1]
		else:
			lps[i] = 0
			i += 1
	return lps

def kmp_search(main_string, pattern):
	M = len(pattern)
	N = len(main_string)
	lps = compute_lps(pattern)
	i = j = 0
	while i < N:
		if pattern[j] == main_string[i]:
			i += 1
			j += 1
		elif j != 0:
			j = lps[j - 1]
		else:
			i += 1
		if j == M:
			return i - j
	return -1

# -------------------------- Рабін-Карп --------------------------

def polynomial_hash(s, base=256, modulus=101):
	n = len(s)
	hash_value = 0
	for i, char in enumerate(s):
		power_of_base = pow(base, n - i - 1) % modulus
		hash_value = (hash_value + ord(char) * power_of_base) % modulus
	return hash_value

def rabin_karp_search(main_string, substring):
	substring_length = len(substring)
	main_string_length = len(main_string)
	base = 256
	modulus = 101
	substring_hash = polynomial_hash(substring, base, modulus)
	current_slice_hash = polynomial_hash(main_string[:substring_length], base, modulus)
	h_multiplier = pow(base, substring_length - 1) % modulus
	for i in range(main_string_length - substring_length + 1):
		if substring_hash == current_slice_hash:
			if main_string[i:i + substring_length] == substring:
				return i
		if i < main_string_length - substring_length:
			current_slice_hash = (current_slice_hash - ord(main_string[i]) * h_multiplier) % modulus
			current_slice_hash = (current_slice_hash * base + ord(main_string[i + substring_length])) % modulus
			if current_slice_hash < 0:
				current_slice_hash += modulus
	return -1

# -------------------------- Порівняння --------------------------

ALGORITHMS = {
	"Боєр-Мур": boyer_moore_search,
	"КМП": kmp_search,
	"Рабін-Карп": rabin_karp_search,
}
BASE_DIR = Path(__file__).parent
ARTICLES = {
	"Стаття 1": (
		BASE_DIR / "стаття 1.txt",
		"Іноді навіть нову проблему можна звести до старої"
	),
	"Стаття 2": (
		BASE_DIR / "стаття 2.txt",
		"Neo4j Documentation"
	),
}
FAKE_PATTERN = "квантовий алгоритм сортування котиків"
NUMBER = 20

def measure(func, text, pattern):
	return timeit.timeit(lambda: func(text, pattern), number=NUMBER) / NUMBER

def run_comparison():
	totals = {name: 0.0 for name in ALGORITHMS}

	for article_name, (path, real_pattern) in ARTICLES.items():
		text = path.read_text(encoding="utf-8")
		print(f"\n{article_name} ({len(text)} символів)")
		print(f"{'Алгоритм':<12} | {'Існуючий, мс':>13} | {'Вигаданий, мс':>13} | {'Сума, мс':>9}")
		print("-" * 57)

		article_totals = {}
		for name, func in ALGORITHMS.items():
			assert func(text, real_pattern) == text.find(real_pattern)
			assert func(text, FAKE_PATTERN) == -1

			t_real = measure(func, text, real_pattern) * 1000
			t_fake = measure(func, text, FAKE_PATTERN) * 1000
			article_totals[name] = t_real + t_fake
			totals[name] += t_real + t_fake
			print(f"{name:<12} | {t_real:>13.4f} | {t_fake:>13.4f} | {t_real + t_fake:>9.4f}")

		fastest = min(article_totals, key=article_totals.get)
		print(f"Найшвидший для «{article_name}»: {fastest}")

	print("-" * 57)
	print("Загальний час по обох статтях:")
	for name, total in sorted(totals.items(), key=lambda item: item[1]):
		print(f"  {name:<12} {total:.4f} мс")
	print(f"Найшвидший в цілому: {min(totals, key=totals.get)}")


if __name__ == "__main__":
	run_comparison()
