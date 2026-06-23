"""
ZTech AI Builder — Complete rebuild.
Generates full PC + peripheral setups per profile.
Pure rule-based (no external API needed).
"""
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from products.models import Product

# ── Constants ────────────────────────────────────────────────────

MIN_BUDGET = 100000   # DZD

# Budget allocation per profile (must sum to 1.0)
PROFILES = {
    'gamer': {
        'label': 'Gaming Build',
        'desc':  'High-performance setup built to dominate at 1080p/1440p with top-tier FPS.',
        'alloc': {'cpu':0.20, 'gpu':0.38, 'ram':0.08, 'storage':0.07,
                  'motherboard':0.10, 'psu':0.06, 'case':0.05,
                  'cooler':0.03, 'monitor':0.00, 'keyboard':0.00, 'mouse':0.03},
    },
    'student': {
        'label': 'Student Build',
        'desc':  'Balanced, power-efficient machine for studying, coding and light creative work.',
        'alloc': {'cpu':0.28, 'gpu':0.12, 'ram':0.12, 'storage':0.12,
                  'motherboard':0.14, 'psu':0.10, 'case':0.06,
                  'cooler':0.04, 'monitor':0.00, 'keyboard':0.00, 'mouse':0.02},
    },
    'creator': {
        'label': 'Creator Build',
        'desc':  'Maximum CPU power and RAM for 4K editing, 3D rendering and content production.',
        'alloc': {'cpu':0.30, 'gpu':0.22, 'ram':0.14, 'storage':0.10,
                  'motherboard':0.10, 'psu':0.06, 'case':0.04,
                  'cooler':0.04, 'monitor':0.00, 'keyboard':0.00, 'mouse':0.00},
    },
    'worker': {
        'label': 'Professional Build',
        'desc':  'Reliable, silent workhorse for multitasking, office work and remote sessions.',
        'alloc': {'cpu':0.32, 'gpu':0.08, 'ram':0.14, 'storage':0.14,
                  'motherboard':0.14, 'psu':0.08, 'case':0.06,
                  'cooler':0.04, 'monitor':0.00, 'keyboard':0.00, 'mouse':0.00},
    },
    'streamer': {
        'label': 'Streaming Build',
        'desc':  'Simultaneous gaming + streaming without dropped frames — dual-role beast.',
        'alloc': {'cpu':0.26, 'gpu':0.34, 'ram':0.10, 'storage':0.08,
                  'motherboard':0.10, 'psu':0.05, 'case':0.04,
                  'cooler':0.03, 'monitor':0.00, 'keyboard':0.00, 'mouse':0.00},
    },
}

# Component type → display label
SLOT_LABELS = {
    'cpu':          'CPU',
    'gpu':          'GPU',
    'ram':          'RAM',
    'storage':      'Storage',
    'motherboard':  'Motherboard',
    'psu':          'PSU',
    'case':         'Case',
    'cooler':       'CPU Cooler',
    'monitor':      'Monitor',
    'keyboard':     'Keyboard',
    'mouse':        'Mouse',
}


# ── Helpers ──────────────────────────────────────────────────────

def _best_for_budget(ctype, budget):
    """Return best product at/under budget for given component_type, or cheapest if nothing fits."""
    qs = Product.objects.filter(
        component_type=ctype, is_active=True, stock__gt=0
    ).order_by('price')
    pick = qs.filter(price__lte=budget).order_by('-price').first()
    return pick or qs.first()


def _serialize(product, label):
    return {
        'slot':     label,
        'id':       product.id,
        'name':     product.name,
        'price':    float(product.price),
        'wattage':  product.wattage or 0,
        'socket':   product.socket or '',
        'ram_type': product.ram_type or '',
        'image':    product.main_image.url if product.main_image else '',
        'slug':     product.slug,
    }


def _compatibility_warnings(components):
    """Return list of warning strings."""
    warnings = []
    by_slot = {c['slot']: c for c in components}

    cpu  = by_slot.get('CPU')
    mobo = by_slot.get('Motherboard')
    ram  = by_slot.get('RAM')
    psu  = by_slot.get('PSU')

    if cpu and mobo:
        if cpu['socket'] and mobo['socket'] and cpu['socket'] != mobo['socket']:
            warnings.append(
                f"Socket mismatch: CPU uses {cpu['socket']} but Motherboard supports {mobo['socket']}."
            )

    if ram and mobo:
        if ram['ram_type'] and mobo['ram_type'] and ram['ram_type'] != mobo['ram_type']:
            warnings.append(
                f"RAM type mismatch: RAM is {ram['ram_type']} but Motherboard supports {mobo['ram_type']}."
            )

    if psu:
        psu_capacity = psu.get('wattage', 0)
        system_watts = sum(c.get('wattage', 0) for c in components if c['slot'] != 'PSU')
        required     = int(system_watts * 1.20)
        if psu_capacity and psu_capacity < required:
            warnings.append(
                f"PSU may be underpowered: system needs ~{required}W (including 20% headroom) but PSU is {psu_capacity}W."
            )

    return warnings


# ── Views ────────────────────────────────────────────────────────

def index(request):
    cpus         = Product.objects.filter(component_type='cpu',         is_active=True, stock__gt=0).order_by('price')
    gpus         = Product.objects.filter(component_type='gpu',         is_active=True, stock__gt=0).order_by('price')
    rams         = Product.objects.filter(component_type='ram',         is_active=True, stock__gt=0).order_by('price')
    storages     = Product.objects.filter(component_type='storage',     is_active=True, stock__gt=0).order_by('price')
    motherboards = Product.objects.filter(component_type='motherboard', is_active=True, stock__gt=0).order_by('price')
    psus         = Product.objects.filter(component_type='psu',         is_active=True, stock__gt=0).order_by('price')
    cases        = Product.objects.filter(component_type='case',        is_active=True, stock__gt=0).order_by('price')
    coolers      = Product.objects.filter(component_type='cooler',      is_active=True, stock__gt=0).order_by('price')
    monitors     = Product.objects.filter(component_type='monitor',     is_active=True, stock__gt=0).order_by('price')
    keyboards    = Product.objects.filter(component_type='keyboard',    is_active=True, stock__gt=0).order_by('price')
    mice         = Product.objects.filter(component_type='mouse',       is_active=True, stock__gt=0).order_by('price')

    context = {
        'cpus': cpus, 'gpus': gpus, 'rams': rams, 'storages': storages,
        'motherboards': motherboards, 'psus': psus, 'cases': cases,
        'coolers': coolers, 'monitors': monitors, 'keyboards': keyboards, 'mice': mice,
        'min_budget': MIN_BUDGET,
    }
    return render(request, 'pages/ai_builder.html', context)


def suggest_build(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data    = json.loads(request.body)
        profile = data.get('profile', 'gamer')
        budget  = int(data.get('budget', MIN_BUDGET))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid request data.'}, status=400)

    if budget < MIN_BUDGET:
        return JsonResponse({
            'success': False,
            'error': f'Minimum budget is {MIN_BUDGET:,} DZD.'
        })

    if profile not in PROFILES:
        profile = 'gamer'

    pdata  = PROFILES[profile]
    alloc  = pdata['alloc']

    components = []
    remaining  = float(budget)

    # Build slot by slot in priority order
    priority_order = ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case', 'cooler', 'monitor', 'keyboard', 'mouse']

    for slot in priority_order:
        if alloc.get(slot, 0) == 0:
            continue
        slot_budget = budget * alloc[slot]
        product     = _best_for_budget(slot, slot_budget)
        if product:
            components.append(_serialize(product, SLOT_LABELS[slot]))

    total    = sum(c['price'] for c in components)
    discount_threshold = getattr(settings, 'CART_DISCOUNT_THRESHOLD', 500000)
    discount = total * 0.10 if total >= discount_threshold else 0
    final    = total - discount
    warnings = _compatibility_warnings(components)

    return JsonResponse({
        'success':    True,
        'suggestion': {
            'label':       pdata['label'],
            'description': pdata['desc'],
            'components':  components,
            'total':       total,
            'discount':    discount,
            'final':       final,
            'warnings':    warnings,
        }
    })


def calculate_build(request):
    """
    POST: {cpu: id, gpu: id, ...}
    Returns total, wattage, PSU recommendation, compatibility verdict.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    selected = {}
    for slot, pid in data.items():
        if not pid:
            continue
        try:
            product = Product.objects.get(id=int(pid), is_active=True)
            selected[SLOT_LABELS.get(slot, slot)] = product
        except (Product.DoesNotExist, ValueError):
            pass

    components = [_serialize(p, label) for label, p in selected.items()]
    total      = sum(c['price'] for c in components)
    watts      = sum(c['wattage'] for c in components)
    psu_rec    = max(int(watts * 1.20), 400)
    warnings   = _compatibility_warnings(components)

    discount_threshold = getattr(settings, 'CART_DISCOUNT_THRESHOLD', 500000)
    discount = total * 0.10 if total >= discount_threshold else 0

    # Overall compatibility verdict
    if not warnings:
        compat = 'compatible'
    elif any('mismatch' in w.lower() or 'underpowered' in w.lower() for w in warnings):
        compat = 'incompatible'
    else:
        compat = 'warning'

    return JsonResponse({
        'total':      total,
        'discount':   discount,
        'final':      total - discount,
        'watts':      watts,
        'psu_rec':    psu_rec,
        'warnings':   warnings,
        'compatible': compat,
        'qualifies_discount': total >= discount_threshold,
    })
