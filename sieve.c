#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#ifdef _MSC_VER
    #define popcount(x) __popcnt64(x)
#endif
#ifdef __GNUC__
    #define popcount(x) __builtin_popcountll(x)
#endif
#define SIEVE_BYTES (128*1024*1024)
#define INNER_LENGTH 8192
// want INNER_LENGTH >= sqrt(SIEVE_BYTES/2)

uint8_t get_bit(uint8_t* arr, size_t bit) {
    return (arr[bit/8] >> (bit%8)) & 1;
}

void set_bit_1(uint8_t* arr, size_t bit) {
    arr[bit/8] |= 1 << (bit%8);
}

void set_bit_0(uint8_t* arr, size_t bit) {
    arr[bit/8] &= ~(1 << (bit%8));
}

void bit_sieve(uint8_t arr[], size_t length) {
    size_t j;
    size_t n;
    // stop when (2i+3)*(2i+3) > 2*8*bound+3
    // 4i^2 + O(i) > 16*bound+O(1)
    // i^2 > 4*bound overshoots a bit but idc
    for (size_t i = 0; i*i <= 4*length; i++) {
        if (!get_bit(arr, i)) { // 2i+3 is prime
            // (2i+3)n is the value of a multiple
            // (2i+3)n = 2j+3, where j is index of that multiple
            // (2i+3)n-3 = 2j
            // j = ((2i+3)n-3)/2
            // check if j/8 is too long
            n = 3; // only care about odd multiples of primes
            j = ((2*i+3)*n-3)/2;
            while (j/8 < length) {
                n += 2;
                set_bit_1(arr, j);
                j = ((2*i+3)*n-3)/2;
            }
        }
    }
}

void bit_sieve_chunks(uint8_t arr[], size_t length, size_t precomputed) {
    size_t j, n;
    for (size_t chunk = 1; chunk*precomputed < length; chunk++) {
        for (size_t i = 0; i < precomputed*8; i++) {
            if (!get_bit(arr, i)) {
                // want n to be an odd number s.t. j is in (or just below) the desired chunk
                // first element in the chunk is chunk*precomputed*8*2 + 3
                // want (chunk*precomputed*16+3)/(2*i+3)
                n = (2*(precomputed*8 * chunk) + 3)/(2*i + 3);
                if (n % 2 == 0) {
                    n -= 1;
                }
                j = ((2*i+3)*n-3)/2;
                while (j/8 < (chunk+1)*precomputed && j/8 < length) {
                    if (2*j+3 < 2*chunk*precomputed*8+3) {
                        n += 2;
                        j = ((2*i+3)*n-3)/2;
                        continue;
                    }
                    n += 2;
                    set_bit_1(arr, j);
                    j = ((2*i+3)*n-3)/2;
                }
            }
        }
    }
}

// should only be used when length is a multiple of 8
size_t count_primes(uint8_t arr[], size_t length) {
    uint64_t* arr64 = (uint64_t*)arr;
    size_t out = 0;
    for (size_t i = 0; i < length/8; i++) {
        out += popcount(arr64[i]);
    }
    return 1+length*8-out;
}

int main(int argc, char const *argv[]) {
    // first we do bit_sieve(arr, O[sqrt(len(arr))] )
    // That should be fast as it'll all fit in cache
    // then we go over the rest of the array in a cache-friendly manner
    uint8_t* arr = calloc(SIEVE_BYTES, sizeof(*arr));
    bit_sieve(arr, INNER_LENGTH); 
    bit_sieve_chunks(arr, SIEVE_BYTES, INNER_LENGTH);
    printf("Number of primes up to %zd:\n", (2*8*(size_t)SIEVE_BYTES)+3);
    printf("%zd\n", count_primes(arr, SIEVE_BYTES));
    free(arr);
    return 0;
}
