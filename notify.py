"""
notify.py — Desktop notification wrapper for EcoTrace AI.
Tries win10toast first; falls back to plyer; silently skips if neither is available.
A failure here NEVER crashes the application.
"""

# TESTED: wrapped in try/except; app continues if toaster fails


def send_toast(title: str, message: str) -> None:
    """Send a desktop notification. Fails silently — never raises."""
    # Attempt 1: win10toast
    try:
        from win10toast import ToastNotifier  # type: ignore
        toaster = ToastNotifier()
        toaster.show_toast(
            title,
            message,
            duration=8,
            threaded=True,
        )
        return
    except ImportError:
        pass  # win10toast not installed; try plyer
    except Exception as e:
        print(f"[notify.py] win10toast error (non-fatal): {e}")

    # Attempt 2: plyer
    try:
        from plyer import notification  # type: ignore
        notification.notify(
            title=title,
            message=message,
            timeout=8,
        )
        return
    except ImportError:
        pass  # plyer not installed; skip silently
    except Exception as e:
        print(f"[notify.py] plyer error (non-fatal): {e}")

    # Final fallback: print to console
    print(f"[notify.py] Notification (no toaster available): [{title}] {message}")
