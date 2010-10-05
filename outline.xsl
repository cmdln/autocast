<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <xsl:for-each select="outline/root/item">
            <xsl:call-template name="item"/>
        </xsl:for-each>
    </xsl:template>
    <xsl:template name="item">
        <xsl:param name="indent"/>
        <xsl:value-of select="$indent"/>
        <xsl:value-of select="values/*[2]/p/run/lit"/>
        <xsl:text>
</xsl:text>
    </xsl:template>
</xsl:stylesheet>
