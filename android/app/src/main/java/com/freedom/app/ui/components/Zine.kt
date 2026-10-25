package com.freedom.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.freedom.app.ui.theme.Zine
import kotlin.math.min

/** Il marchio: cerchio spezzato in alto, la freccia di download lo attraversa ed esce sotto. */
@Composable
fun FreedomMark(modifier: Modifier = Modifier, color: Color = Zine.Spray, size: Dp = 48.dp) {
    Canvas(modifier.size(size)) {
        val s = min(this.size.width, this.size.height)
        val stroke = s * 0.075f
        val r = s * 0.315f
        drawArc(
            color, startAngle = -62f, sweepAngle = 304f, useCenter = false,
            topLeft = Offset(s / 2 - r, s * 0.52f - r), size = Size(2 * r, 2 * r), style = Stroke(stroke),
        )
        drawLine(color, Offset(s * 0.5f, s * 0.04f), Offset(s * 0.5f, s * 0.88f), stroke, StrokeCap.Square)
        drawLine(color, Offset(s * 0.31f, s * 0.70f), Offset(s * 0.5f, s * 0.89f), stroke, StrokeCap.Square)
        drawLine(color, Offset(s * 0.69f, s * 0.70f), Offset(s * 0.5f, s * 0.89f), stroke, StrokeCap.Square)
    }
}

/** Timbro storto, tipo etichetta di nastro adesivo. */
@Composable
fun Stamp(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = Zine.Spray,
    rotation: Float = -4f,
) {
    Text(
        text = text.uppercase(),
        style = MaterialTheme.typography.labelMedium,
        color = color,
        modifier = modifier
            .rotate(rotation)
            .border(2.dp, color)
            .padding(horizontal = 8.dp, vertical = 3.dp),
    )
}

/** Bottone pieno con ombra netta sfalsata: niente ripple morbidi, solo blocchi. */
@Composable
fun PunkButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    container: Color = Zine.Acid,
    content: Color = Zine.Toner,
    shadow: Color = Zine.Spray,
    enabled: Boolean = true,
) {
    Box(modifier.padding(end = 5.dp, bottom = 5.dp)) {
        Box(
            Modifier
                .matchParentSize()
                .offset(5.dp, 5.dp)
                .background(if (enabled) shadow else Zine.Concrete)
        )
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier
                .background(if (enabled) container else Zine.Concrete)
                .border(2.dp, Zine.Toner)
                .clickable(enabled = enabled, onClick = onClick)
                .padding(horizontal = 16.dp, vertical = 12.dp),
        ) {
            if (icon != null) {
                Icon(icon, contentDescription = null, tint = content, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(8.dp))
            }
            Text(text.uppercase(), style = MaterialTheme.typography.labelLarge, color = content)
        }
    }
}

/** Chip filtro come un pezzo di nastro: attivo = evidenziatore, inattivo = contorno. */
@Composable
fun TapeChip(text: String, selected: Boolean, onClick: () -> Unit, modifier: Modifier = Modifier) {
    Text(
        text = text.uppercase(),
        style = MaterialTheme.typography.labelMedium,
        color = if (selected) Zine.Toner else Zine.Paper,
        modifier = modifier
            .background(if (selected) Zine.Acid else Color.Transparent)
            .border(1.5.dp, if (selected) Zine.Acid else Zine.Smudge)
            .clickable(onClick = onClick)
            .padding(horizontal = 10.dp, vertical = 6.dp),
    )
}

fun formatDuration(ms: Long): String {
    if (ms <= 0) return "--:--"
    val totalSec = ms / 1000
    val h = totalSec / 3600
    val m = (totalSec % 3600) / 60
    val s = totalSec % 60
    return if (h > 0) "%d:%02d:%02d".format(h, m, s) else "%d:%02d".format(m, s)
}
